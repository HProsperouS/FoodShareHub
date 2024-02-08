# import third-party libraries
import html
from fastapi import (
    WebSocket, 
    Request,
)
from fastapi.responses import ORJSONResponse
import orjson

# import local Python libraries
from utils import constants as C
from db.models.chat import (
    Message,
    Conversation,
)
from db.crud.chat_crud import (
    get_sendername_of_unread_messages,
    get_latest_messages_for_user,
    get_opposite_users,
)
from aws.services import (
    retreive_user,
    list_cognito_user_by_usernames,
)
from sqlalchemy.orm import Session
from sqlalchemy import func, or_, and_

# import Python's standard libraries
import html
import time
import base64
import pathlib
import asyncio
import hashlib
import logging
from typing import Any
from zoneinfo import ZoneInfo
from datetime import datetime


chat_mutex = asyncio.Lock()
async def add_user_to_connected_list(websocket: WebSocket, user_id: str) -> None:
    """Add the user to the list of connected users for cleanup.

    Args:
        websocket (WebSocket):
            The websocket object that will be used to get the FastAPI app.
        user_id (str):
            The user's id.

    Returns:
        None:
    """
    async with chat_mutex:
        # add the user to the list of connected users
        websocket.app.state.chat_connected_users.add(user_id)

async def remove_user_from_connected_list(websocket: WebSocket, user_id: str) -> None:
    """Removes the user to the list of connected users.

    Args:
        websocket (WebSocket):
            The websocket object that will be used to get the FastAPI app.
        user_id (str):
            The user's id.

    Returns:
        None:
    """
    async with chat_mutex:
        # remove the user from the list of connected users
        websocket.app.state.chat_connected_users.remove(user_id)

# async def get_chat_notifications(username: str, db_session) -> list[dict]:
#     """Get all the unread chats for the user using RDS in a synchronous way.

#     Args:
#         user_id (int):
#             The user id.
#         db_session:
#             The SQLAlchemy session object.

#     Returns:
#         list[dict]:
#             The list of unread chats.
#     """
#     # Get Unread Messages Sender Username
#     senders = await get_sendername_of_unread_messages(db_session, username)

#     # Get User Information by Sender Username
#     if senders:
#         users = list_cognito_user_by_usernames(senders)
        
#         return [
#             {
#                 "Username": user.username,
#                 "display_name": user.display_name,
#                 "profile_image": user.profile_image_url,
#             } 
#             for user in users
#         ]
#     else:
#         return []

async def send_chat_list(ws: WebSocket, user_doc: dict, db_session):
    # Step 1: Get all the chat sessions that the user has or has received messages from, Get the latest message for each chat session
    senderUsername = user_doc['Username']
    chats = await get_latest_messages_for_user(db_session, senderUsername) # This contains the latest message for each chat session but can be null if there is no chat session
    # print("Chats List", chats)
    user_dict = {}

    # Step 2: Get the opposite users information for the chats
    opposite_users = await get_opposite_users(db_session, senderUsername)
    user_names = {user.Participant1 for user in opposite_users} | {user.Participant2 for user in opposite_users}
    user_names.discard(user_doc['Username'])  # remove the current user's Username
    users = list_cognito_user_by_usernames(user_names)
    user_dict = {user["Username"]: user for user in users}
    
    # Step 3: Construct the chat data
    formatted_chats = []
    
    for chat in chats:
        opposite_user = chat.Receiver if chat.Sender == senderUsername else chat.Sender 
        opposite_user = user_dict.get(opposite_user)
        # print("opposite_user", opposite_user)

        receiver_username = ""

        if chat.Sender == senderUsername:
            receiver_username = "You"
        else:
            receiver_username = opposite_user["Username"]
            
        formatted_dict = {
            "Username": opposite_user.get("Username"),
            "UserId": opposite_user.get("UserId"),
            "ProfileImage": opposite_user.get("Username"),
        }

        if chat.Type == "text":
            formatted_dict["message"] = f"{receiver_username}: {chat.Content}"
        # else: # file
            # if chat["message"] and decrypted_msg is not None:
            #     formatted_dict["message"] = f"{receiver_username}: {decrypted_msg}"
            # else:
            #     formatted_dict["message"] = f"{receiver_username} sent {'a file' if len(chat['files']) == 1 else 'multiple files'}."

        # Things to include is the user online status and profile image
        formatted_dict["_id"] = str(chat.Sender)
        formatted_dict["display_name"] = opposite_user["Username"]
        formatted_dict["username"] = opposite_user["Username"]
        # formatted_dict["online"] = opposite_user.get("chat", {"online": False})["online"]
        formatted_dict["timestamp"] = chat.SendTime
        formatted_dict["profile"] = opposite_user["Attributes"][2]["Value"]
        formatted_dict["message_id"] = str(chat.Id)
        formatted_dict["conversation_id"] = chat.ConversationId
        formatted_dict["is_read"] = chat.IsRead
        formatted_chats.append(format_json_response(formatted_dict))

    # print("formatted_chats", formatted_chats)
    # Step 4： Send the data
    await ws.send_json({"chats": formatted_chats})

def datetime_to_unix_time(datetime_obj: datetime) -> float:
    """Converts a datetime object to a Unix timestamp.

    Args:
        datetime_obj (datetime):
            The datetime object to convert.

    Returns:
        float:
            The Unix timestamp.
    """
    return datetime_obj.replace(tzinfo=ZoneInfo("UTC")).timestamp()

def __format_value_for_json(value: Any, escape: bool | None = True) -> Any:
    """Format the value for JSON deserialisation/dumps.

    Args:
        value (Any):
            The value to format.
        escape (bool, optional):
            Whether to escape the value. Defaults to True.

    Returns:
        Any:
            The formatted value.
    """
    if isinstance(value, str) and escape:
        return html.escape(value)

    if isinstance(value, datetime):
        return value.isoformat()
    
    if isinstance(value, bytes):
        return base64.b64encode(value).decode("utf-8")

    if isinstance(value, dict):
        return {key: __format_value_for_json(value, escape=escape) for key, value in value.items()}

    if isinstance(value, list):
        return [__format_value_for_json(item, escape=escape) for item in value]

    return value

def format_json_response(value: Any, escape: bool | None = True, dump_json: bool | None = False) -> Any:
    """Format the value for JSON deserialisation/dumps.

    Args:
        value (Any):
            The value to format.
        escape (bool, optional):
            Whether to escape the value. Defaults to True.
        dump_json (bool, optional):
            Whether to dump the value to JSON. Defaults to False.

    Returns:
        Any:
            The formatted value.
    """
    formatted_value = __format_value_for_json(value, escape=escape)
    return orjson.dumps(formatted_value).decode("utf-8") if dump_json else formatted_value

def model_to_dict(model_instance):
    return {column.name: getattr(model_instance, column.name) for column in model_instance.__table__.columns}


