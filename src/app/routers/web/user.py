# import third-party libraries
from fastapi import (
    APIRouter,
    Request,
    Depends,
)
from fastapi.responses import (
    HTMLResponse,
    RedirectResponse,
)

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
