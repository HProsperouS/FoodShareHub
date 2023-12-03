# import third-party libraries
from fastapi import (
    APIRouter,
    Request,
    Form,
    HTTPException,
    Response
)
from fastapi.responses import (
    HTMLResponse,
    RedirectResponse,
)
# from pydantic import BaseModel
from typing import Annotated
import boto3
import uuid
# import aioredis

# import local libraries
from utils.jinja2_helper import (
    flash, 
    render_template,
)
# import utils.constants as C
from fastapi.templating import Jinja2Templates

# import env
import os
from dotenv import load_dotenv

load_dotenv()

# redis cached endpoint
# redis_pool = aioredis.from_url("testcache-ampw1p.serverless.use1.cache.amazonaws.com:6379")
    
authentication_router = APIRouter(
    include_in_schema=True,
    prefix="/authentication",
    tags= ['Authentication']
)


COGNITO_USER_POOL_ID = os.environ.get("COGNITO_USER_POOL_ID")
COGNITO_CLIENT_ID = os.environ.get("COGNITO_CLIENT_ID")
COGNITO_HOSTED_UI = os.environ.get("COGNITO_HOSTED_UI")

client = boto3.client('cognito-idp',region_name = 'us-east-1')

# NOTES 
# Need to fix prefix path cuz cant go to / if prefix is authentication
# Need to add in redis to store session
# Need to retrieve the user role with admin_get_user in login 
# Not sure how to use access token
# Need to use rbac 

@authentication_router.post("/signup")
async def signup(request:Request, username: Annotated[str, Form()], password: Annotated[str, Form()], email: Annotated[str,Form()], role: Annotated[str,Form()]) -> RedirectResponse:
    response = client.sign_up(
        ClientId = COGNITO_CLIENT_ID,
        Username = username,
        Password = password,
        UserAttributes=[
            {'Name': 'email', 'Value': email},
            {"Name": "custom:role", "Value": role}
        ]
    )

    print(response)

    confirmation_code = client.resend_confirmation_code(
        ClientId= COGNITO_CLIENT_ID,
        Username = username
    )

    print(confirmation_code)

    request.session["temp"] = username

    return RedirectResponse(url="/authentication/confirmation",status_code=303)


@authentication_router.get("/confirmation")
async def confirmation_get(request: Request) -> RedirectResponse:
    try:
        if request.session.get("temp") is None:
            return RedirectResponse(url="/authentication",status_code=303)
        else:
            return await render_template(
                name="authentication/signup_confirmation.html",
                context={
                    "request": request,
                },
            )
    except Exception as e:
        print(e)
        


@authentication_router.post("/confirmation")
async def confirmation_post(request: Request, code: Annotated[str, Form()]) -> RedirectResponse:
    try:
        username : str = request.session["temp"]
        confirm_code = client.confirm_sign_up(
            ClientId = COGNITO_CLIENT_ID,
            Username = username,
            ConfirmationCode = code
        )

        flash(
            request=request,
            message=f"Successfully activated account : {username}", 
            category="success",
        )

        request.session.pop("temp")
        
        
        return RedirectResponse(url="/authentication",status_code=303)

    except Exception as e:
        print(e)

@authentication_router.post("/login")
async def login(request:Request,password: Annotated[str, Form(...,min_length=6)], username: Annotated[str,Form()],) -> RedirectResponse:
    
    try:
        login = client.initiate_auth(
        AuthFlow="USER_PASSWORD_AUTH",
        AuthParameters={
            "USERNAME": username,
            "PASSWORD": password,
        },
        ClientId=COGNITO_CLIENT_ID
        )
        print(login)

        # tokens for short interactions ( not sure how use )
        access_token = login['AuthenticationResult']['AccessToken']

        # create user session id
        session_id = str(uuid.uuid4())

        # set the session 
        request.session["session"] = {
        "session_id" : session_id,
        "user_id": username,
        "access_token": access_token,
        "role": "User"   
        }

        print(request.session["session"])

        flash(
            request=request,
            message=f"You are logged in as {username}", 
            category="success",
        )
        
        return RedirectResponse(url="/authentication",status_code=303)

    except Exception as e:
        print(e)
        return RedirectResponse(url="/authentication",status_code=303)

@authentication_router.post("/logout")
async def logout(request: Request) -> RedirectResponse:
    
    try:
        if request.session["session"]:
            request.session.pop("session")

        flash(
        request=request,
        message="You have logged out successfully", 
        category="success",
        )

        return RedirectResponse("/authentication", status_code=303)

    except Exception as e:
        print(e)



@authentication_router.get("/")
async def index(request: Request) -> RedirectResponse:
    try:
        if request.session.get("session") is None:
            
            return await render_template(
                name="authentication/authentication.html",
                context={
                    "request": request,
                },
            )
        else:
            return RedirectResponse(url="/foodshare/addMyListing", status_code=303)
    except Exception as e:
        print(e)
