# import third-party libraries
from fastapi import (
    APIRouter,
    Request,
    Depends,
    Query
)
from fastapi.responses import (
    HTMLResponse,
    RedirectResponse
)
from fastapi.encoders import jsonable_encoder

from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date
import os, boto3
from botocore.exceptions import ClientError 

# import local libraries
from utils.jinja2_helper import (
    flash, 
    render_template,
)
from db import (
    # DB Session
    get_db,
)
from utils import constants as C
from depends import (
    rbac
)
from aws.services import (
    retreive_user,
)

from db.crud.chat_crud import (
    create_conversation
)

RBAC_DEPENDENCY = Depends(rbac.USER_RBAC, use_cache=False)


chat_router = APIRouter(
    include_in_schema=False,
    prefix="/chat",
    tags=["Chat"],
)

@chat_router.get("/{receiver_id}/{receiver_name}")
async def chat_1_to_1(request: Request, receiver_id: str, receiver_name: str, rbac_res: rbac.RBACResults | RedirectResponse = RBAC_DEPENDENCY , db: Session = Depends(get_db)):
    if not isinstance(rbac_res, rbac.RBACResults):
        return rbac_res

    """
        Step 1: Check if the receiver is exist
        Step 2: Check if the sender is the same as receiver
        Step 3: Check if the sender has the permission to chat with the receiver
        Step 4: Check if the receiver has the permission to chat with the sender
        Step 5: Check if the receiver has blocked the sender
        Step 6: Check if the sender has blocked the receiver
    """
    receiver = retreive_user(receiver_name)
    if receiver == "fail":
        # TODO Redirect to error page
        return RedirectResponse(url="/")

    # Extracting Receiver Username, UserId, and EmailAddress
    receiver_doc = {
        'Username': receiver['Username'],
        'UserId': next((attr['Value'] for attr in receiver['UserAttributes'] if attr['Name'] == 'sub'), None),
        'EmailAddress': next((attr['Value'] for attr in receiver['UserAttributes'] if attr['Name'] == 'email'), None)
    }

    # Extracting Sender Username, UserId, and EmailAddress
    session = request.session.get(C.SESSION_COOKIE, None)
    sender_doc = {
        'Username': session["username"],
        'UserId': session["user_id"],
        'EmailAddress': session["email"]
    }

    # Check if the sender is the same as receiver
    # TODO Redirect to error page
    if sender_doc['UserId'] == receiver_doc['UserId']: # cannot chat with yourself
        return RedirectResponse(url="/")
    
    # Create the conversation if it doesn't exist
    await create_conversation(
        db=db,
        sender=sender_doc['Username'],
        receiver=receiver_doc['Username']
    )

    return await render_template(
        name="chat/chat.html",
        context={
            "request": request,
            "sender": sender_doc,
            "receiver": receiver_doc,
        }
    )



