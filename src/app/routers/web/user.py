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

import pyotp
import qrcode

from aws.services import (
    generate_software_token,
    verify_software_token
)

# Class Objects
class MFASetupCode(BaseModel):
    AccessToken: str
    Session:str
    Code:str

user_router = APIRouter(
    include_in_schema=True,
    tags= ["User"]
)
RBAC_DEPENDS = Depends(USER_RBAC, use_cache=False)

@user_router.get("/usertest")
async def usertest(request: Request, rbac_res: RBAC_TYPING = RBAC_DEPENDS) -> HTMLResponse:
    if not isinstance(rbac_res, RBACResults):
        print(rbac_res.headers)
        return rbac_res

    return await render_template(
        name="index.html",
        context={
            "request": request,
        },
    )

@user_router.get("/user/account/")
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
def enablemfa(request:Request) -> ORJSONResponse:
    try:
        print("start")
        name = request.session.get("session")["username"]
        session = request.session.get("session")["session_id"]
        print("2")
        # generate associate token to verify later
        associate = generate_software_token(session=session)

        session = associate["Session"]
        verify_access_token = associate["SecretCode"]

        print("Start generating qr code")

        otp = pyotp.TOTP(verify_access_token)
        auth_str = otp.provisioning_uri(name=name,issuer_name="FoodShareHub")

        qrImg = qrcode.make(auth_str)

        imgPath = f'C:\\TEMP_Y3S2\\Enterprise_Cloud_Project\\FoodShareHub\\src\\app\\static\\{request.session.get("session")["user_id"]}_mfa_qr.png'

        qrImg.save(imgPath)

        print("imgPath: "+imgPath)

        print("QR Code generated")  
    
        return ORJSONResponse(
            content={"qr_code": imgPath,"access_token":verify_access_token,"session":session,"status":"success"}
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

        verify = verify_software_token(access_token,session,code)

        request.session.get("session")["mfa"] = "Enabled"

        return ORJSONResponse(
            content={"status":"success"}
        )
    
    except Exception as e:
        print(e)

        return ORJSONResponse(
            content={"status":"fail"}
        )