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
    GUEST_RBAC,
    RBAC_TYPING,
    RBACResults
)

guest_router = APIRouter(
    include_in_schema=False,
    tags= ["Guest"]
)
RBAC_DEPENDS = Depends(GUEST_RBAC, use_cache=False)

@guest_router.get("/login")
async def login(request: Request, rbac_res: RBAC_TYPING = RBAC_DEPENDS) -> HTMLResponse:
    if not isinstance(rbac_res, RBACResults):
        return rbac_res
    return {"action_required": "login"}
