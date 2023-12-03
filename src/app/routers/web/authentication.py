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
from pydantic import BaseModel

# import local libraries
from utils.jinja2_helper import (
    flash, 
    render_template,
)
from typing import Annotated
import boto3
from fastapi.security import OAuth2AuthorizationCodeBearer

import jwt
import uuid
from datetime import datetime, timedelta

import utils.constants as C

from fastapi.templating import Jinja2Templates


# import aioredis

# redis cached endpoint
# redis_pool = aioredis.from_url("testcache-ampw1p.serverless.use1.cache.amazonaws.com:6379")

# from botocore.exceptions import ClientError

# import requests

# from cryptography.hazmat.backends import default_backend
# from cryptography.hazmat.primitives import serialization

class User(BaseModel):
    name: str
    password: str 
    email: str
    

authentication_router = APIRouter(
    include_in_schema=True,
    prefix='/authentication',
    tags= ['Authentication']
)
COGNITO_USER_POOL_ID = 'us-east-1_SF8HCGjKa'
COGNITO_CLIENT_ID = 'amt4io534vb3t7q48nggdgquk'
COGNITO_HOSTED_UI = 'https://test-fsh.auth.us-east-1.amazoncognito.com'
client = boto3.client('cognito-idp',region_name = 'us-east-1')

# username = "testuser"
# password = "123456"

# @authentication_router.get("/authentication")
# async def get_login_link():
#     login_link = f"{COGNITO_HOSTED_UI}?response_type=code&client_id={COGNITO_CLIENT_ID}&redirect_uri=http://127.0.0.1:8000/callback"
#     return await {"login_link": login_link}

@authentication_router.post("/signup")
async def signup(request:Request, username: Annotated[str, Form()], password: Annotated[str, Form()], email: Annotated[str,Form()], role: Annotated[str,Form()]) -> RedirectResponse:
    response = client.sign_up(
        ClientId = COGNITO_CLIENT_ID,
        Username = username,
        # Username = user.username
        Password = password,
        # Password = user.password
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
    return await render_template(
        name="authentication/signup_confirmation.html",
        context={
            "request": request,
            
        },
    )


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


# @authentication_router.get("/testroute")
# async def test(request:Request) -> RedirectResponse:
#     login = client.initiate_auth(
#     AuthFlow="USER_PASSWORD_AUTH",
#     AuthParameters={
#         "USERNAME": "1",
#         "PASSWORD": "1",
#     },
#     ClientId=COGNITO_CLIENT_ID
#     )
#     print(login)

#     return await render_template(
#         name="authentication/authentication.html",
#         context={
#             "request": request,
            
#         },
#         )

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
        "role": "User" # Temp role for testing
        # "role": role
   
        }

        print(request.session.get("session"))

        flash(
            request=request,
            message=f"You are logged in as {username}", 
            category="success",
        )
        
        return RedirectResponse(url="/authentication",status_code=303)
        
        

        



    except Exception as e:
        print(e)
        # if auth fails, returns auth page & validation errors
        return await render_template(
        name="authentication/authentication.html",
        context={
            "request": request,
            
        },
        )
        






# # Login endpoint - Creates a new session
# @router.post("/login")
# def login(user: dict = Depends(authenticate_user)):
#     session_id = create_session(user["user_id"])
#     return {"message": "Logged in successfully", "session_id": session_id}

# def authenticate_user(credentials: HTTPBasicCredentials = Depends(security)):
#     user = users.get(credentials.username)
#     if user is None or user["password"] != credentials.password:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Invalid credentials",
#             headers={"WWW-Authenticate": "Basic"},
#         )
#     return user

# def create_session(user_id: int):
#     session_id = len(sessions) + random.randint(0, 1000000)
#     sessions[session_id] = user_id
#     return session_id

# # Protected endpoint - Requires authentication
# @router.get("/protected")
# def protected_endpoint(user: dict = Depends(get_authenticated_user_from_session_id)):
#     if user is None:
#         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authenticated")
#     return {"message": "This user can connect to a protected endpoint after successfully autheticated", "user": user}


# # Get current user endpoint - Returns the user corresponding to the session ID
# @router.get("/getusers/me")
# def read_current_user(user: dict = Depends(get_user_from_session_id)):
#     return user

# # Custom middleware for session-based authentication
# def get_authenticated_user_from_session_id(request: Request):
#     session_id = request.cookies.get("session_id")
#     if session_id is None or int(session_id) not in sessions:
#         raise HTTPException(
#             status_code=401,
#             detail="Invalid session ID",
#         )
#     # Get the user from the session
#     user = get_user_from_session(int(session_id))
#     return user

# # Use the valid session id to get the corresponding user from the users dictionary
# def get_user_from_session(session_id: int):
#     user = None
#     for user_data in users.values():
#         if user_data['user_id'] == sessions.get(session_id):
#             user = user_data
#             break

#     return user
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

        return  RedirectResponse("/authentication", status_code=303)

    except Exception as e:
        print(e)

    

    # return await render_template(
    #     name="authentication/authentication.html",
    #     context={
    #         "request": request,
    #     },
       
    # )



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
            print(request.session.get("session"))
            
            

            redis_pool.close()
            await redis_pool.wait_closed()

            return await render_template(
                name="authentication/Test.html",
                context={
                    "request": request,
                },
            )
    except:
         return await render_template(
                name="authentication/Test.html",
                context={
                    "request": request,
                },
            )
