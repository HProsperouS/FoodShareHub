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

RBAC_DEPENDENCY = Depends(rbac.USER_RBAC, use_cache=False)


chat_router = APIRouter(
    include_in_schema=False,
    prefix="/chat",
    tags=["Chat"],
)

@chat_router.get("/")
async def chat(request: Request, rbac_res: rbac.RBACResults | RedirectResponse = RBAC_DEPENDENCY, db:Session = Depends(get_db)) :    
    return await render_template(
        name="chat/chat.html",
        context={
            "request": request,
        },
    )



