# import third-party libraries
from fastapi import (
    APIRouter,
    Depends,
    Request,
    Form,
    HTTPException,
    Response
)
from fastapi.responses import (
    HTMLResponse,
    RedirectResponse,
)

from typing import Annotated
# from FoodShareHub.src.app.middleware.JWTAuth import JWTAuthorizationCredentials, JWTBearer, get_jwks
import boto3
import uuid
# from redis import asyncio as aioredis
# import local libraries
from utils.jinja2_helper import (
    flash, 
    render_template,
)
# import utils.constants as C
from fastapi.templating import Jinja2Templates
# from boto3.exceptions import CognitoIdentityProviderError
# import env
import os
from dotenv import load_dotenv
from botocore.exceptions import ClientError
# import hmac
# import hashlib
# import base64
load_dotenv()

# TODO Remember to pip install setuptools
# TODO Remember to pip install redis>=4.2.0rc1
# global redis cached endpoint
# redis_pool = aioredis.from_url("redis://demo-redis.ampw1p.ng.0001.use1.cache.amazonaws.com:6379")
    
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
# Need JWT token
# MFA - Need to get secret_hash from the sign up and use it as setup key for MFA. and se

def create_session(request:Request, username: str,role:str,user_id:str,email:str):
    session_id = str(uuid.uuid4())

    request.session["session"] = {
        "session_id" : session_id,
        "username": username,
        "user_id":user_id,
        "email":email,
        "role": role   
        }

    # redis_conn = await aioredis.create_redis_pool(redis_pool)

    # await redis_conn.setsetex(username,600,session_id)

    # redis_conn.close()
    # await redis_conn.wait_closed()
    
    return "Session created"

def authenticate_user(username: str,password: str):

    try:
        login = client.initiate_auth(
            AuthFlow="USER_PASSWORD_AUTH",
            AuthParameters={
                "USERNAME": username,
                "PASSWORD": password,
            },
            ClientId=COGNITO_CLIENT_ID
            )
        return login
    except ClientError as e:
        print(e)

def mfa_setup(username:str,session:str,access_token:str,code:str):
    try:
        print("verify token")
        verify = client.verify_software_token(AccessToken=access_token,Session=session,UserCode=code)

        return verify
    except Exception as e:
        print(e)
        return "Unsuccessful"


def multifactor_auth(username:str,code:str,session:str):
    try:
        response = client.respond_to_auth_challenge(
            ClientId=COGNITO_CLIENT_ID,
            ChallengeName="SOFTWARE_TOKEN_MFA",
            ChallengeResponses={
                'USERNAME': username,  # Provide the user's username or email
                'SOFTWARE_TOKEN_MFA_CODE': code,
            },
            Session=session,
        )

        return response
    except Exception as e :
        print(e)
        return "Unsuccessful"



@authentication_router.post("/signup")
async def signup(request:Request, username: Annotated[str, Form()], password: Annotated[str, Form()], email: Annotated[str,Form()], role: Annotated[str,Form()]) -> RedirectResponse:
    try:
        response = client.sign_up(
            ClientId = COGNITO_CLIENT_ID,
            # SecretHash=
            Username = username,
            Password = password,
            UserAttributes=[
                {'Name': 'email', 'Value': email},
                {"Name": "custom:role", "Value": role}
            ]
        )
        print(response)

        confirmation_mail = client.resend_confirmation_code(
            ClientId= COGNITO_CLIENT_ID,
            Username = username
        )

        print(confirmation_mail)

        request.session["account_confirmation"] = username

        flash(
            request=request,
            message=f"Please check your email for confirmation code", 
            category="success",
            )

        return RedirectResponse(url="/authentication/confirmation",status_code=303)
    
    # need set proper invalid input exceptions
    except Exception as e: 

        print(e) 

        flash(
            request=request,
            message=f"Password needs to be at least 6 characters", 
            category="danger",
            )
        
        return RedirectResponse(url="/authentication/",status_code=303) 

@authentication_router.get("/confirmation")
async def confirmation_get(request: Request) -> RedirectResponse:
    try:
        if request.session.get("account_confirmation") is None and request.session.get("login_mfa") is None:
            return RedirectResponse(url="/authentication",status_code=303)
        else:
            print("check5")
            return await render_template(
                name="authentication/confirmation.html",
                context={
                    "request": request,
                },
            )
    except Exception as e:
        print(e)
        print("check6")
        
@authentication_router.post("/confirmation")
async def confirmation_post(request: Request, code: Annotated[str, Form()]) -> RedirectResponse:
    try:
        print("checking")
        if request.session.get("account_confirmation") is not None:
            username : str = request.session["account_confirmation"]
            
            confirmation = client.confirm_sign_up(
                ClientId = COGNITO_CLIENT_ID,
                Username = username,
                ConfirmationCode = code
            )

            print(confirmation)

            flash(
                request=request,
                message=f"Successfully activated account : {username}", 
                category="success",
            )

            request.session.clear()

        if request.session.get("login_mfa") is not None:

            print("mfa")
            challenge = request.session.get("login_mfa")["challengename"]
            username = request.session.get("login_mfa")["username"]
            session = request.session.get("login_mfa")["session"]
            access_token = request.session.get("login_mfa")["access_token"]

            if challenge == "MFA_SETUP":
                print("Setup")
                mfa = mfa_setup(username=username,session=session,access_token=access_token,code=code)
                if mfa != "Unsuccessful":
                    request.session.clear()
            elif challenge == "SOFTWARE_TOKEN_MFA":
                mfa = multifactor_auth(username=username,code=code,session=session)
                if mfa != "Unsuccessful":
                    request.session.clear()
                    get_user = client.get_user(AccessToken=mfa["AuthenticationResult"]["AccessToken"])
                    print(get_user)
                    user_attributes = get_user["UserAttributes"]
                    role = "N/A"
                    for attribute in user_attributes:
                        if attribute["Name"] == "rolecustom:role":
                            role = attribute["Value"]
                    
                    create_session(username=username,role=role,request=request)

            print(mfa)

            

            if mfa == "Unsuccessful":
                flash(
                    request=request,
                    message=f"Invalid code, Please try again", 
                    category="danger",
                )
                return RedirectResponse(url="/authentication/confirmation",status_code=303)
            else:        
                flash(
                    request=request,
                    message=f"Successfully authenticate : {username}", 
                    category="success",
                    )
        
        return RedirectResponse(url="/authentication",status_code=303)

    except Exception as e:
        print(e)


# auth = JWTBearer(get_jwks())
# # retrieve username from JWT
# async def get_current_user(
#     credentials: JWTAuthorizationCredentials = Depends(auth)
# ) -> str:
#     try:
#         return credentials.claims["username"]
#     except KeyError:
#         HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Username missing")

    
@authentication_router.post("/login")
async def login(request:Request,password: Annotated[str, Form(...,min_length=6)], username: Annotated[str,Form()],) -> RedirectResponse:
    
    try:
        print("Authenticating")
        auth_user = authenticate_user(username,password)
        print(auth_user)

        print("check 1")
        
        # session = auth_user["Session"]
        # challengename = auth_user["ChallengeName"]
        # access_token = "N/A"
        # print("check 2")
        # if challengename == "MFA_SETUP":
        #     associate = client.associate_software_token(Session=session)
        #     session = associate["Session"]
        #     access_token = associate["SecretCode"]
        #     request.session["mfa_setup_key"] = access_token
        #     print(associate)
        
        # print("check 3")
        # request.session["login_mfa"] = {'username':username,"session":session,"challengename":challengename,"access_token":access_token}
        # print("check 4")
        get_user = client.get_user(AccessToken=auth_user["AuthenticationResult"]["AccessToken"])
        print(get_user)
        user_attributes = get_user["UserAttributes"]
        role = "N/A"
        email="N/A"
        id = "N/A"
        for attribute in user_attributes:
            if attribute["Name"] == "rolecustom:role":
                role = attribute["Value"]
            if attribute["Name"] == "email":
                email = attribute["Value"]
            if attribute["Name"] == "sub":
                id = attribute["Value"]
        create_session(username=username,role=role,request=request,email=email,user_id=id) 
        print(request.session["session"])
        return RedirectResponse(url="/authentication/confirmation",status_code=303)

    except Exception as e:
        print(e)

        flash(
            request=request,
            message="Incorrect username or password", 
            category="danger",
        )

        return RedirectResponse(url="/authentication",status_code=303)

      

@authentication_router.post("/logout")
async def logout(request: Request) -> RedirectResponse:
    
    try:
        if request.session["session"]:
            username = request.session["session"]["user_id"]

            request.session.pop("session")

            # redis_conn = await aioredis.create_redis_pool(redis_pool)

            # await redis_conn.delete(username)

            # redis_conn.close()
            # await redis_conn.wait_closed
            

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
