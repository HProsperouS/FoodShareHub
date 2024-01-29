# import third-party libraries
from fastapi import (
    APIRouter,
    Request,
    Form,
    Query,
    Depends,
    WebSocket,
    WebSocketDisconnect,
    UploadFile,
)
from fastapi.responses import (
    RedirectResponse,
    ORJSONResponse,
)
from pydantic import ValidationError
from sqlalchemy.orm import Session
from websockets.exceptions import WebSocketException

# import local libraries
from utils.helper import (
    decode_base64_file
)
from utils import constants as C
from utils import helper as Helper
from db import (
    # Chat
    get_messages_for_user,
    get_message_by_id_and_sender,
    delete_message_by_id,
    insert_message,
)
from utils.chat import (
    add_user_to_connected_list,
)
from db.dependencies import get_db
from db. models.chat import (
    Message,
    Conversation
)
from aws.services import(
    upload_to_s3,
    detect_objects,
    detect_objects_and_moderate,
    retreive_user
)
from utils.chat import (
    send_chat_list,
    format_json_response,
    model_to_dict,
)
# import Python's standard libraries
from depends import (
    rbac
)
import asyncio
from datetime import datetime


chat_api = APIRouter(
    include_in_schema=True,
    prefix=C.API_PREFIX,
    tags=["chat"],
)
RBAC_DEPENDENCY = Depends(rbac.USER_RBAC, use_cache=False)


@chat_api.websocket("/ws/{receiver_uid}/{receiver_name}")
async def chat_ws(websocket: WebSocket, receiver_uid: str, receiver_name: str, db: Session = Depends(get_db)):
    """
        Step 1: Check if the receiver is exist
        Step 2: Check if the sender is the same as receiver
    """
    print("connected")
    await websocket.accept()

    # Extracting Sender Username, UserId, and EmailAddress
    sender_doc = await get_info_from_session(websocket)
    print(sender_doc)
    if sender_doc['UserId'] == receiver_uid:
        return await websocket.close(reason="Sorry! You can't chat with yourself even if you're that lonely.")

    receiver = retreive_user(receiver_name)
    if receiver == "fail":
        return await websocket.close(reason="No such user exists.")
    
    # Extracting Receiver Username, UserId, and EmailAddress
    receiver_doc = {
        'Username': receiver['Username'],
        'UserId': next((attr['Value'] for attr in receiver['UserAttributes'] if attr['Name'] == 'sub'), None),
        'EmailAddress': next((attr['Value'] for attr in receiver['UserAttributes'] if attr['Name'] == 'email'), None)
    }
    
    print("receiver_doc", receiver_doc)
    # Get Chat Lists
    await send_chat_list(
        ws=websocket,
        user_doc=sender_doc,
        db_session=db,
    )

    # Get the messages from the database
    fetch_initial_messages = await websocket.receive_json()
    print("fetch_initial_messages", fetch_initial_messages)
    if fetch_initial_messages.get("fetch_initial_messages"):
        # if the user is opening the chat for the first time on their browser.
        # Doesn't necessarily mean that the user is opening a new chat session.
        messages = await get_messages_for_user(db, sender_doc['Username'], receiver_doc['Username'])
        print("messages", messages)
        if not messages:
            await websocket.send_json({"new_chat_session": True})
    else:
        # if the user is reconnecting.
        msg = await get_messages_for_user(db, sender_doc['Username'], receiver_doc['Username'])

    try:
        await add_user_to_connected_list(
            websocket=websocket,
            user_id=sender_doc["UserId"],
        )
        while True:
            # TODO
            # Update the current user (sender) status to online
            new_messages = await get_messages_for_user(db, sender_doc['Username'], receiver_doc['Username'])
            if new_messages:
                latest_msg = new_messages[-1]

            # Send the new messages to the client
            for message_doc in new_messages:
                await websocket.send_json(format_json_response(message_doc, escape=False))
            
            # Send Latest Chat Lists
            await send_chat_list(
                ws=websocket,
                user_doc=sender_doc,
                db_session=db,
            )

            # TODO Check if the user is blocked

            try:
                # wait for new messages from the client
                receive_user_msg_task = asyncio.create_task(
                    websocket.receive_json(),
                )
                _, pending = await asyncio.wait(
                    [receive_user_msg_task],
                    timeout=1.5,
                )
            except: # on unix system, an exception is raised
                raise WebSocketDisconnect(1001, "Connection closed by client.")

            # Cancel the pending task if there was no new message from the client.
            # This is so that the user would receive any new messages from the opposite user in the database via polling.
            for task in pending:
                task.cancel()
            if pending:
                continue
            
            data = receive_user_msg_task.result()
            print("data HERE", data)

            # Delete Messsaage
            delete_msg = data.get("delete", False)
            if delete_msg:
                # if user is requesting to delete a message...
                chat_doc = await get_message_by_id_and_sender(db, delete_msg)
                if chat_doc is None:
                    continue

                message_type: str = chat_doc.Type

                # If the message is not a text message, delete the file from the S3 bucket
                if message_type != "text":
                    deletion_tasks = []
                    # TODO Delete file from S3
                    # for file in chat_doc["files"]:
                    #     deletion_tasks.append(
                    #         upload_to_s3.delete_object(
                    #             bucket=C.PRIVATE_BUCKET,
                    #             key=file["blob_name"]
                    #         )
                    #     )
                    # await asyncio.gather(*deletion_tasks)

                await delete_message_by_id(db, delete_msg)

                continue

            # Check if the message is valid
            msg = data.get("message")

            conversation_id = data.get("conversation_id")
            if msg is None:
                continue
            if not isinstance(msg, str):
                await websocket.send_json({
                    "error": "Your message must be a string.",
                })
                continue
            msg = msg.strip()
            if len(msg) < 1:
                continue
            
            #TODO Check if the message is too long
            # if len(msg) > 1000:

            # Insert Message into Database, and Update the Conversation LastMessageId and LastMessageTime
            new_message = Message(
                Sender=sender_doc['Username'],
                Receiver=receiver_doc['Username'],
                Content=msg,
                Type="text",
                IsRead=False,
                ConversationId=conversation_id
            )
            messageId = await insert_message(db, new_message, conversation_id)
            new_message.Id = messageId
            
            new_message_dict = model_to_dict(new_message)
            await websocket.send_json(format_json_response(new_message_dict, escape=False))
            await insert_message(db, new_message)
            
    except (WebSocketDisconnect, WebSocketException):
        print("ERROR.FOUND IN WEBSOCKET")

async def get_info_from_session(
    request: Request | WebSocket
) -> dict :
    session = request.session.get(C.SESSION_COOKIE, None)

    sender_doc = {
        'Username': session["username"],
        'UserId': session["user_id"],
        'EmailAddress': session["email"]
    }
    
    return sender_doc