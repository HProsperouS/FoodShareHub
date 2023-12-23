# import third-party libraries
from fastapi import (
    APIRouter,
    Request,
    Depends,
)
from fastapi.responses import (
    HTMLResponse,
    ORJSONResponse,
    RedirectResponse,
)
from pydantic import BaseModel
import os
from dotenv import load_dotenv
import boto3
from aws.services.Cognito import *
import uuid
# import local libraries
from utils.jinja2_helper import (
    flash, 
    render_template,
)
from depends import (
    GUEST_RBAC,
    RBAC_TYPING,
    RBACResults
)
load_dotenv()

guest_router = APIRouter(
    include_in_schema=True,
    tags= ["Guest"]
)
# User Objects
class ExistingUser(BaseModel):
    Name: str
    Password: str

class NewUser(BaseModel):
    Name:str
    Password:str
    Email:str
    Role:str

class RegisterConfirmation(BaseModel):
    Code:str
    
RBAC_DEPENDS = Depends(GUEST_RBAC, use_cache=False)

def create_session(request:Request, username: str,role:str,user_id:str,email:str):
    session_id = str(uuid.uuid4())

    request.session["session"] = {
        "session_id" : session_id,
        "username": username,
        "user_id":user_id,
        "email":email,
        "role": role   
        }

    # TODO Use Redis to store sessions
    # redis_conn = await aioredis.create_redis_pool(redis_pool)
    # await redis_conn.setsetex(username,600,session_id)
    # redis_conn.close()
    # await redis_conn.wait_closed()
    
    return "session created"

@guest_router.get("/login")
async def login(request: Request, rbac_res: RBAC_TYPING = RBAC_DEPENDS) -> HTMLResponse:
    print(RBACResults)
    if not isinstance(rbac_res, RBACResults):
        print(rbac_res.headers)
        return rbac_res
    
    return await render_template(
        name="authentication/login.html",
        context={
            "request": request,
        },
    )

@guest_router.post("/login")
async def login(request: Request,formData:ExistingUser, rbac_res: RBAC_TYPING = RBAC_DEPENDS) -> ORJSONResponse:
    
    try:
        # user credentials
        name = formData.Name
        password = formData.Password

        # authenticate user
        auth_user = authenticate_user(name,password)

        # retrieve user information
        accesstoken = auth_user["AuthenticationResult"]["AccessToken"]
        get_user = retreive_user(accesstoken)

        # retreive user attributes
        user_attributes = get_user["UserAttributes"]
        attributes = {"id":"","email":"","role":""}
        for attribute in user_attributes:
            if attribute["Name"] == "custom:role":
                attributes["role"] = attribute["Value"]
            if attribute["Name"] == "email":
                attributes["email"] = attribute["Value"]
            if attribute["Name"] == "sub":
                attributes["id"] = attribute["Value"]

        # create session
        role = attributes["role"]
        email= attributes["email"]
        id = attributes["id"]
        create_session(username=name,role=role,request=request,email=email,user_id=id) 

        return ORJSONResponse(
            content={"redirect_url": "http://127.0.0.1:8000/foodshare/myListings","status":"success"}
        )
        
    except Exception as e :
        print(e)

        return ORJSONResponse(
            content={"redirect_url": "http://127.0.0.1:8000/login","status":"fail"}
        )




@guest_router.get("/register")
async def register(request: Request, rbac_res: RBAC_TYPING = RBAC_DEPENDS) -> HTMLResponse:
    if not isinstance(rbac_res, RBACResults):
        return rbac_res

    return await render_template( 
        name="authentication/register.html",
        context={
            "request": request,
        },
    )

        
@guest_router.post("/register")
async def register(request: Request,formData:NewUser, rbac_res: RBAC_TYPING = RBAC_DEPENDS) -> ORJSONResponse:
    
    try:
        # user credentials
        name = formData.Name
        password = formData.Password
        email = formData.Email
        role = formData.Role

        # create user
        create_user = register_user(name,password,email,role)

        # temp store account confirmation
        request.session["account_confirmation"] = name

        return ORJSONResponse(
            content={"redirect_url": "http://127.0.0.1:8000/register/confirmation","status":"success"}
        )
    
    except Exception as e :
        print(e)

        return ORJSONResponse(
            content={"redirect_url": "http://127.0.0.1:8000/register","status":"fail"}
        )
    
@guest_router.get("/register/confirmation")
async def confirmation(request: Request, rbac_res: RBAC_TYPING = RBAC_DEPENDS) -> RedirectResponse:
    if not isinstance(rbac_res, RBACResults):
        return rbac_res
    
    try:
        if request.session.get("account_confirmation") is None:
            return RedirectResponse(url="/foodshare/MyListings",status_code=303)
        else:
            return await render_template(
                name="authentication/register_confirmation.html",
                context={
                    "request": request,
                },
            )
    except Exception as e:
        print(e)

@guest_router.post("/register/confirmation")
async def confirmation(request: Request,formData:RegisterConfirmation, rbac_res: RBAC_TYPING = RBAC_DEPENDS) -> ORJSONResponse:
    try:
       # credentials
       code = formData.Code
       name = request.session.get("account_confirmation")
       
       # account confirmation
       confirmation = register_confirmation(name,code)

       # clear session
       request.session.clear()

       return ORJSONResponse(
            content={"redirect_url": "http://127.0.0.1:8000/login","status":"success"}
       )

    except Exception as e:
       print(e)