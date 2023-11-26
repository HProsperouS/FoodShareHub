# import third-party libraries
from fastapi import (
    APIRouter,
    Request,
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

foodshare_router = APIRouter(
    include_in_schema=False,
    prefix='/foodshare',
    tags= ['FoodSharingPlatform']
)

@foodshare_router.get("/add")
async def index(request: Request) -> RedirectResponse:
    flash(
        request=request,
        message="This is a test flash message", 
        category="test",
    )
    return await render_template(
        name="foodshare/addDonation.html",
        context={
            "request": request,
        },
    )