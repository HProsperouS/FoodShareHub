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
    ALLROLES_RBAC,
    RBAC_TYPING,
    RBACResults,
)

allroles_router = APIRouter(
    include_in_schema=False,
    tags= ["AllRoles"]
)
RBAC_DEPENDS = Depends(ALLROLES_RBAC, use_cache=False)

@allroles_router.get("/")
async def index(request: Request, rbac_res: RBAC_TYPING = RBAC_DEPENDS) -> HTMLResponse:
    if not isinstance(rbac_res, RBACResults):
        return rbac_res

    flash(
        request=request,
        message="This is a test flash message", 
        category="success",
    )
    return await render_template(
        name="index.html",
        context={
            "request": request,
        },
    )
