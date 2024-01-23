# import third-party libraries
from io import BytesIO
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

# import local libraries
from utils.jinja2_helper import (
    flash, 
    render_template,
)
from depends import (
    USER_RBAC,
    RBAC_TYPING,
    RBACResults,
)
from aws.services import (
    edit_user_information,
    reset_password,
    disable_account,
    upload_qrcode_to_s3,
    delete_s3_object,
    upload_userimage_to_s3,
    authenticate_user
)
from utils import constants as C
import pyotp
import qrcode

from aws.services import (
    generate_software_token,
    verify_software_token
)

from aws.services import(
    upload_to_s3,
)

from utils.helper import (
    decode_base64_file
)
from utils import constants as C

# Class Objects
class MFASetupCode(BaseModel):
    AccessToken: str
    Session:str
    Code:str

class UserImage(BaseModel):
    FileName: str
    ContentType: str
    Size: int
    Base64: str

class EditUser(BaseModel):
    Email: str
    Image: UserImage

class ResetPassword(BaseModel):
    CurrentPassword: str
    NewPassword: str

class MFAPassword(BaseModel):
    Password:str

user_router = APIRouter(
    include_in_schema=True,
    tags= ["User"]
)
RBAC_DEPENDS = Depends(USER_RBAC, use_cache=False)

# @user_router.get("/usertest")
# async def usertest(request: Request, rbac_res: RBAC_TYPING = RBAC_DEPENDS) -> HTMLResponse:
#     if not isinstance(rbac_res, RBACResults):
#         print(rbac_res.headers)
#         return rbac_res

#     return await render_template(
#         name="index.html",
#         context={
#             "request": request,
#         },
#     )

@user_router.get("/user/account")
async def account(request: Request, rbac_res: RBAC_TYPING = RBAC_DEPENDS) -> HTMLResponse:
    if not isinstance(rbac_res, RBACResults):
        return rbac_res
            
    return await render_template( 
        name="user/account.html",
        context={
            "request": request,
        },
    )

@user_router.post("/logout")
async def logout(request: Request) -> RedirectResponse:
    
    try:
        request.session.clear()

        return RedirectResponse("/login", status_code=303)
    except Exception as e:
        print(e)

@user_router.post("/enablemfa")
def enablemfa(request:Request, formData:MFAPassword) -> ORJSONResponse:
    try:
        bucket_name = C.S3_BUCKET_NAME 
        name = request.session.get("session")["username"]
        session = request.session.get("session")["session_id"]
        password = formData.Password
        # generate associate token to verify later
        try:
            associate = generate_software_token(session=session)
        except Exception as e:
            newsession = authenticate_user(name,password)
            session =  newsession["Session"]
            associate = generate_software_token(session=session)

        session = associate["Session"]
        verify_access_token = associate["SecretCode"]

        print("Start generating QR Code")

        otp = pyotp.TOTP(verify_access_token)
        auth_str = otp.provisioning_uri(name=name,issuer_name="FoodShareHub")
        qrImg = qrcode.make(auth_str)
        imgPath = "uploads/" + name + "_qrcode.png"

        publicAccessURL = f"https://{bucket_name}.s3.amazonaws.com/{imgPath}"

        buffer = BytesIO()
        qrImg.save(buffer, "PNG")
        buffer.seek(0) 

        upload = upload_qrcode_to_s3(buffer,imgPath)

        print("QR Code generated")  
    
        return ORJSONResponse(
            content={"qr_code":publicAccessURL ,"access_token":verify_access_token,"session":session,"status":"success"}
        )

    except Exception as e:
        print(e)

        return ORJSONResponse(
            content={"qr_code": "N/A","access_token":"N/A","session":"N/A","status":"fail"}
        )

@user_router.post("/verifymfa")
def verifymfa(request:Request,formData:MFASetupCode) -> ORJSONResponse:
    try:

        access_token = formData.AccessToken
        session = formData.Session
        code = formData.Code
        username = request.session.get("session")["username"]
        verify = verify_software_token(access_token,session,code)

        if verify == "fail":
            return ORJSONResponse(
                content={"status":"fail"}
            )

        request.session.get("session")["mfa"] = "Enabled"

        path = "uploads/" + username + "_qrcode.png"
        delete = delete_s3_object(path)

        return ORJSONResponse(
            content={"status":"success"}
        )
    
    except Exception as e:
        print(e)

        return ORJSONResponse(
            content={"status":"fail"}
        )

@user_router.post(path="/user/account/editInformation")
async def edit_information(request:Request, formData:EditUser) -> ORJSONResponse:
    try:
        # Temp S3 Info
        bucket_name = C.S3_BUCKET_NAME

        session = request.session.get("session")
        username = session["username"]
        email = session["email"]
        publicAccessURL = "N/A"
        try:    
            user_filename= username + "_" + formData.Image.FileName
            file = decode_base64_file(formData.Image.Base64)
            
            if upload_userimage_to_s3(file, user_filename, bucket_name, formData.Image.ContentType):
                print("Image uploaded to S3 successfully")
            else:
                return ORJSONResponse(content={"error": "Failed to upload image to S3"}, status_code=500)
            
            publicAccessURL = f"https://{bucket_name}.s3.amazonaws.com/user/{user_filename}"
        except Exception as e:
            print(e)

        # Update user profile attributes
        updated_user = edit_user_information(username,email,publicAccessURL)

        if updated_user == "fail":
            return ORJSONResponse(
                content={"status":"fail"}
            )
        
        request.session["session"]["image"] = publicAccessURL

        return ORJSONResponse(
            content={"image":publicAccessURL,"status":"success"}
        )
    
    except Exception as e :
        print(e)
        return ORJSONResponse(
            content={"status":"fail"}
        )

@user_router.post(path="/user/password/reset")
async def reset_user_password(request:Request, formData:ResetPassword) -> ORJSONResponse:
    try:
        current_pass = formData.CurrentPassword
        new_pass = formData.NewPassword
        access_token = request.session["session"]["session_id"]

        reset = reset_password(current_pass,new_pass,access_token)

        if reset == "fail":
            return ORJSONResponse(
                content={"status":"fail"}
            )
        
        return ORJSONResponse(
            content={"status":"success"}
        )
    


    except Exception as e:
        print(e)
        return ORJSONResponse(
            content={"status":"fail"}
        )

@user_router.post(path="/user/account/disable")
async def reset_user_password(request:Request) -> ORJSONResponse:
    try:

        username = request.session["session"]["username"]
        reset = disable_account(username)

        if reset == "fail":
            return ORJSONResponse(
                content={"status":"fail"}
            )
        
        return ORJSONResponse(
            content={"status":"success"}
        )
    
    except Exception as e:
        print(e)
        return ORJSONResponse(
            content={"status":"fail"}
        )
