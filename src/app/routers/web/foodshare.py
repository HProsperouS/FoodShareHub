from fastapi import Request, APIRouter
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
# from .web_utils import render_template

templates = Jinja2Templates(directory="templates")

foodshare_router = APIRouter(
    prefix='/foodshare',
    tags= ['FoodSharingPlatform']
)

# @router.get("/foodshare/add", response_class=HTMLResponse)
# async def fooditem_add(request: Request):

#     return await render_template(
#         name="admin/mod_dashboard.html",
#         context={
#         },
#     )

@foodshare_router.get("/add", response_class=HTMLResponse)
async def donation_add(request: Request):
    return templates.TemplateResponse("foodshare/addDonation.html", {"request": request})