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
    filler_task
)
from utils import constants as C
from utils import helper as Helper
from db import (
    # Notifications
    get_messages_for_user,
)

from utils.chat import (
    get_chat_notifications,
    get_info_from_session
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
    retreive_user,
    analyze_comprehend_toxicity
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

from schemas.request.chat import ( 
    ChatMessage
)

user_api = APIRouter(
    include_in_schema=True,
    prefix=C.API_PREFIX,
    tags=["users"],
)

@user_api.get(
    path="/get/notifications",
    description="Retrieve the list of notifications for the current user.",
)
async def get_notifications(
    request: Request,
    db: Session = Depends(get_db),
):
    # Extracting Sender Username, UserId, and EmailAddress
    user_doc = await get_info_from_session(request)
    # Extract Unread Messages with the Sender's Username
    unread_msg = await get_chat_notifications(username=user_doc["Username"],db=db) 

    print(unread_msg)

    num_of_unread = 0
    num_of_unread = len(unread_msg)

    if num_of_unread > 1:
        msg_suffix = msg_suffix = unread_msg[0]["Username"] + f" and {num_of_unread - 1} other"
    elif num_of_unread == 1:
        msg_suffix = unread_msg[0]["Username"]
    
    data = {
        "users": unread_msg,
        "message": f"You have unread messages from {msg_suffix}" if num_of_unread > 0 else "You have no unread messages",
    }
    
    return format_json_response(data)