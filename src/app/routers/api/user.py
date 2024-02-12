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
    path="/user/getNotifications",
    description="Retrieve the list of notifications for the current user.",
)
async def get_notifications(
    request: Request,
    db: Session = Depends(get_db),
):
    # Extracting Sender Username, UserId, and EmailAddress
    user_doc = await get_info_from_session(request)
    print(user_doc["Username"])

    # Extract Unread Messages with the Sender's Username
    unread_msg_users = await get_chat_notifications(username=user_doc["Username"], db_session=db) 
    print(unread_msg_users) # Sample output: ['tzy', 'ljj', 'declan']

    # Construct notifications data
    notifications = [
        {
            "username": notification,
            "message": f"You have an unread message from {notification}"
        }
        for notification in unread_msg_users
    ]

    print(notifications)
    
    return ORJSONResponse(notifications)