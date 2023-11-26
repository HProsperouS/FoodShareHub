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
    include_in_schema=False,
    tags= ["User"]
)
RBAC_DEPENDS = Depends(USER_RBAC, use_cache=False)

@user_router.get("/usertest")
async def usertest(request: Request, rbac_res: RBAC_TYPING = RBAC_DEPENDS) -> HTMLResponse:
    if not isinstance(rbac_res, RBACResults):
        return rbac_res
    
    return await render_template(
        name="index.html",
        context={
            "request": request,
        },
    )
