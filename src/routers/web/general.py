# import third-party libraries
from fastapi import (
    APIRouter,
    Request,
)
from fastapi.responses import (
    RedirectResponse,
)

# import local libraries
from utils.jinja2_helper import (
    flash, 
    render_template,
)

general_router = APIRouter(
    include_in_schema=False,
    prefix="",
)

@general_router.get("/")
async def index(request: Request) -> RedirectResponse:
    return await render_template(
        name="general/index.html",
        context={
            "request": request,
        },
    )

@general_router.get("/testflash")
async def testflash(request: Request) -> RedirectResponse:
    flash(
        request=request,
        message="This is a test flash message", 
        category="test",
    )
    return RedirectResponse(url="/")
