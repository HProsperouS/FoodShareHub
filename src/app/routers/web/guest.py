# import third-party libraries
from fastapi import (
    APIRouter,
    Request,
    Depends,
    Query
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
import redis
import datetime
from aws.services import (
    register_user,
    register_confirmation,
    retreive_user,
    authenticate_user,
    login_mfa,
    edit_google_user_information,
    update_last_access,
    verify_email_address,
    update_online_status,
    get_current_user_location,
    login_attempts
)
import jwt
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
import socket
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

class LoginMfa(BaseModel):
    Name:str
    Password:str
    Code:str

class AccessToken(BaseModel):
    Token:str

class UserLocation(BaseModel):
    Longitude:float
    Latitude:float

import uuid
    
RBAC_DEPENDS = Depends(GUEST_RBAC, use_cache=False)


def create_session(request:Request, username: str,role:str,user_id:str,email:str,session_id:str,mfa:str,image:str,status:str):
    request.session["session"] = {
        "session_id" : session_id,
        "username": username,
        "user_id":user_id,
        "email":email,
        "role": role,
        "mfa": mfa,
        "image":image,
        'status':status
        }
    
    return "success"

@guest_router.post("/getusercurrentlocation")
async def getUserCurrentLocation(request:Request, formData:UserLocation) -> ORJSONResponse:

    longitude = formData.Longitude
    latitude = formData.Latitude

    user_location = get_current_user_location(longitude,latitude)

    return ORJSONResponse(
        content={"user_location": user_location}
    ) 

@guest_router.post("/googleurl")
async def googleurl(request: Request) -> ORJSONResponse:

    google_login_url = 'https://foodsharehub.auth.ap-southeast-1.amazoncognito.com/oauth2/authorize?identity_provider=Google&redirect_uri=http://localhost:8000/login&response_type=TOKEN&client_id=7uq1jl7tbrcg525aeddpg0hhev&scope=email openid profile'

    return ORJSONResponse(
        content={"redirect_url": google_login_url}
    ) 

@guest_router.get("/login")
async def login(request: Request, rbac_res: RBAC_TYPING = RBAC_DEPENDS) -> HTMLResponse:
    # print(RBACResults)
    if not isinstance(rbac_res, RBACResults):
        print(rbac_res.headers)
        return rbac_res
    
    return await render_template(
        name="authentication/login.html",
        context={
            "request": request,
        },
    )

@guest_router.post("/googlelogin")
async def googlelogin(request: Request, formData:AccessToken) -> ORJSONResponse:

    try:
        base_url = str(request.base_url)

        # TODO Need a way to get the info for google , missing secret key
        # TODO Need a way to revoke access token
        decoded_jwt = jwt.decode(formData.Token,algorithms=['RS256'],options={"verify_signature": False})  
        print(decoded_jwt)
        username = decoded_jwt["username"]
        get_user = retreive_user(username)
        user_attr = {}
        print(get_user)

        # Just check whether attributes have been added
        check_counter = 0 
        for attr in get_user["UserAttributes"]:
            if attr["Name"] == "email":
                user_attr["temp_username"] = attr["Value"].split('@')[0]
                user_attr["email"] = attr['Value']
            if attr["Name"] == "sub":
                user_attr["id"] = attr['Value']
            if attr["Name"] == "custom:image":
                check_counter += 1
                user_attr["image"] = attr['Value']
            if attr["Name"] == "custom:role":
                check_counter += 1
                user_attr["role"] = attr['Value']
        if check_counter < 2:
            edit_google_user_information(username,"N/A","User")

            # Create session
            temp_username = user_attr["temp_username"]
            role = "User"
            email= user_attr["email"]
            id = user_attr["id"]
            session = formData.Token
            image = 'N/A'
            mfa = "Enabled"
            status = 'Online'

        else:

            # Create session
            temp_username = user_attr["temp_username"]
            role = user_attr["role"]
            email= user_attr["email"]
            id = user_attr["id"]
            session = formData.Token
            image = user_attr["image"]
            mfa = "Enabled"
            status='Online'

        create_session(username=username,role=role,request=request,email=email,user_id=id,session_id=session,mfa=mfa,image=image,status=status)
        print(request.get("session"))
        # current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # update_last_access(username,current_time)
        return ORJSONResponse(
            content={"redirect_url": f"{base_url}","status":"success"}
            
        ) 
    except Exception as e :
        print(e)

        return ORJSONResponse(
            content={"redirect_url": f"{base_url}","status":"fail"}
        )

@guest_router.post("/login")
async def login(request: Request,formData:ExistingUser, rbac_res: RBAC_TYPING = RBAC_DEPENDS) -> ORJSONResponse:
    
    try:
        base_url = str(request.base_url)
        # User credentials
        name = formData.Name
        password = formData.Password

        # Authenticate user
        auth_user_list = authenticate_user(name,password)
        print(auth_user_list)
        auth_user = auth_user_list[0]
        auth_error = auth_user_list[1]

        hostname = socket.gethostname()
        ip_address = socket.gethostbyname(hostname)
        
        if auth_user == "fail" :
            user_attempts = login_attempts(ip_address,name)
            if user_attempts == "too many attempts":
                return ORJSONResponse(
                    content={"redirect_url": f"{base_url}login","status":"too many attempts"}
                )
            return ORJSONResponse(
                content={"redirect_url": f"{base_url}login","status":"fail","error":auth_error}
            )
        elif auth_user == "account disabled":
            return ORJSONResponse(
                content={"redirect_url": f"{base_url}login","status":"account disabled"}
            )
        elif auth_user["ChallengeName"] == "SOFTWARE_TOKEN_MFA":
            request.session["temp_session"] = auth_user["Session"]
            
            return ORJSONResponse(
                content={"name":name,"password":password,"status":"success","mfa":"Enabled"}
            )
        else:
            # Get user info
            get_user = retreive_user(name)
            if get_user == 'fail':
                return ORJSONResponse(
                    content={"redirect_url": f"{base_url}login","status":"fail","error":"fail to retrieve user"}
                )
            # Retreive user attributes
            user_attributes = get_user["UserAttributes"]
            attributes = {"id":"","email":"","role":""}
            for attribute in user_attributes:
                if attribute["Name"] == "custom:role":
                    attributes["role"] = attribute["Value"]
                if attribute["Name"] == "email":
                    attributes["email"] = attribute["Value"]
                if attribute["Name"] == "sub":
                    attributes["id"] = attribute["Value"]
                if attribute["Name"] == "custom:image":
                    attributes["image"] = attribute["Value"]

            # Create session
            role = attributes["role"] 
            email= attributes["email"] 
            id = attributes["id"] 
            session = auth_user["Session"]
            image = attributes["image"]
            mfa = "Disabled"
            status = "Online"

            create_session(username=name,role=role,request=request,email=email,user_id=id,session_id=session,mfa=mfa,image=image,status=status)
            
            print(request.session.get("session"))
            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            update_last_access(name,current_time)
            update_online_status(name,"Online")


            return ORJSONResponse(
                content={"redirect_url": f"{base_url}foodshare/myListings","status":"success","mfa":"Disabled"}
            ) 
        # return ORJSONResponse(
        #     content={"redirect_url": "http://127.0.0.1:8000/foodshare/myListings","status":"success"}
        # ) 
    except Exception as e :
        print(e)

        return ORJSONResponse(
            content={"redirect_url": f"{base_url}login","status":"fail",'error':str(e)}
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
        base_url = str(request.base_url)
        # User credentials
        name = formData.Name
        password = formData.Password
        email = formData.Email
        role = formData.Role
        image = "N/A"

        # detect type of language and offensive language
        client = boto3.client("comprehend",region_name = "ap-southeast-1")
        detect_text = client.detect_sentiment(Text=name, LanguageCode="en")
        detect_language = client.detect_dominant_language(Text=name)
        
        if detect_text["Sentiment"] == "NEGATIVE":
            print(detect_text)
            return ORJSONResponse(
                content={"redirect_url": f"{base_url}register","status":"fail","text_analysis":detect_text["Sentiment"]}
            )
        languageBoolean = False
        language_type = ""
        for language in detect_language["Languages"]:
            if language["LanguageCode"] == "en":
                language_type = language["LanguageCode"]
                languageBoolean = True
                
        if languageBoolean == True:
            # Create user
            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            create_user = register_user(name,password,email,role,image,current_time)
            print(create_user)

            if create_user == "fail":
                # Redirect to register page but the container IP keeps changing every deployment
                return ORJSONResponse(
                    content={"redirect_url": f"{base_url}register","status":"fail","message":"User already exists"}
                )

            # temp store account confirmation
            request.session["account_confirmation"] = name

            verify_ses_email = verify_email_address(email)
            print(verify_ses_email)

            return ORJSONResponse(
                content={"redirect_url": f"{base_url}register/confirmation","status":"success","language_analysis":language_type}
            )
        elif languageBoolean == False:
            language_type = "ch"
            return ORJSONResponse(
                content={"redirect_url": f"{base_url}register","status":"fail","language_analysis":language_type}
            )

    except Exception as e :
        print(e)

        return ORJSONResponse(
            content={"redirect_url": f"{base_url}register","status":"fail"}
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
       base_url = str(request.base_url)
       # Account confirmation credentials
       code = formData.Code
       name = request.session.get("account_confirmation")
       
       # Account confirmation
       confirmation = register_confirmation(name,code)

       if confirmation == "fail":
           return ORJSONResponse(
            content={"status":"fail"}
           )
       
       request.session.clear()

       return ORJSONResponse(
            content={"redirect_url": f"{base_url}login","status":"success"}
       )

    except Exception as e:
       print(e)



@guest_router.post("/login/mfa")
async def loginMfa(request: Request,formData:LoginMfa, rbac_res: RBAC_TYPING = RBAC_DEPENDS) -> ORJSONResponse:
    try:
        session = request.session.get("temp_session")
    except Exception as e:
        session = request.session.get("session")["session_id"]
    try:
        base_url = str(request.base_url)
        code = formData.Code
        name = formData.Name
        password = formData.Password

        challenge = login_mfa(code,session,name)

        if challenge == "fail":
            # Create a new session to authenticate code again
            new_session = authenticate_user(name,password)["Session"]

            request.session["temp_session"] = new_session

            challenge = login_mfa(code,new_session,name)


        get_user = retreive_user(name)
        # Retreive user attributes
        user_attributes = get_user["UserAttributes"]
        attributes = {"id":"","email":"","role":""}
        for attribute in user_attributes:
            if attribute["Name"] == "custom:role":
                attributes["role"] = attribute["Value"]
            if attribute["Name"] == "email":
                attributes["email"] = attribute["Value"]
            if attribute["Name"] == "sub":
                attributes["id"] = attribute["Value"]
            if attribute["Name"] == "custom:image":
                attributes["image"] = attribute["Value"]


        # Create session
        role = attributes["role"] 
        email= attributes["email"] 
        id = attributes["id"] 
        image = attributes["image"]
        access_token = challenge["AuthenticationResult"]["AccessToken"]
        status = "Online"

        create_session(username=name,role=role,request=request,email=email,user_id=id,session_id=access_token,mfa="Enabled",image=image,status=status)
        print(request.session.get("session"))

        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
        update_last_access(name,current_time)
        update_online_status(name,"Online")

        print("User is now online")
    
        return ORJSONResponse(
            content={"redirect_url": f"{base_url}foodshare/myListings","status":"success"}
        ) 
    except Exception as e:
        print(e)

        return ORJSONResponse(
            content={"redirect_url": f"{base_url}login","status":"fail"}
        )