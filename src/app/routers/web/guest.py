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
from aws.services import (
    register_user,
    register_confirmation,
    retreive_user,
    authenticate_user,
    login_mfa
)
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

class LoginMfa(BaseModel):
    Name:str
    Password:str
    Code:str
    
RBAC_DEPENDS = Depends(GUEST_RBAC, use_cache=False)

def create_session(request:Request, username: str,role:str,user_id:str,email:str,session_id:str,mfa:str,image:str):
    # session_id = str(uuid.uuid4())

    request.session["session"] = {
        "session_id" : session_id,
        "username": username,
        "user_id":user_id,
        "email":email,
        "role": role,
        "mfa": mfa,
        "image":image
        }
    
    return "success"
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
        # User credentials
        name = formData.Name
        password = formData.Password

        # Authenticate user
        auth_user = authenticate_user(name,password)
        print(auth_user)

        if auth_user == "fail" :
            return ORJSONResponse(
                content={"redirect_url": "http://127.0.0.1:8000/login","status":"fail"}
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
                    content={"redirect_url": "http://127.0.0.1:8000/login","status":"fail"}
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

            create_session(username=name,role=role,request=request,email=email,user_id=id,session_id=session,mfa=mfa,image=image)
            print(request.session.get("session"))
            
            return ORJSONResponse(
                content={"redirect_url": "http://127.0.0.1:8000/foodshare/myListings","status":"success","mfa":"Disabled"}
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
        # User credentials
        name = formData.Name
        password = formData.Password
        email = formData.Email
        role = formData.Role
        image = "N/A"

        # Create user
        create_user = register_user(name,password,email,role,image)
        print(create_user)

        if create_user == "fail":
            return ORJSONResponse(
                content={"redirect_url": "http://127.0.0.1:8000/register","status":"fail","message":"User already exists"}
            )

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
            content={"redirect_url": "http://127.0.0.1:8000/login","status":"success"}
       )

    except Exception as e:
       print(e)

@guest_router.post("/login/mfa")
async def loginMfa(request: Request,formData:LoginMfa, rbac_res: RBAC_TYPING = RBAC_DEPENDS) -> ORJSONResponse:
    try:
        session = request.session.get("temp_session")
        code = formData.Code
        name = formData.Name
        password = formData.Password

        challenge = login_mfa(code,session,name)

        if challenge == "fail":
            # Create a new session to authenticate code again
            new_session = authenticate_user(name,password)["Session"]

            request.session["temp_session"] = new_session
            return ORJSONResponse(
                content={"status":"fail"}
            ) 


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

        create_session(username=name,role=role,request=request,email=email,user_id=id,session_id=access_token,mfa="Enabled",image=image)
        print(request.session.get("session"))
        
        return ORJSONResponse(
            content={"redirect_url": "http://127.0.0.1:8000/foodshare/myListings","status":"success"}
        ) 
    except Exception as e:
        print(e)

        return ORJSONResponse(
            content={"redirect_url": "http://127.0.0.1:8000/login","status":"fail"}
        )