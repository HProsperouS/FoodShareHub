# import third-party libraries
from fastapi import (
    APIRouter,
    Request,
    Depends,
    HTTPException,
    Form,
    File,
    UploadFile
)
from fastapi.responses import (
    HTMLResponse,
    RedirectResponse,
    JSONResponse
)
from sqlalchemy.orm import Session
from datetime import date
import os, boto3
from botocore.exceptions import ClientError 

# import local libraries
from utils.jinja2_helper import (
    flash, 
    render_template,
)
from db.crud.fooditem_crud import add_fooditem, get_all_fooditems, get_fooditem_by_id, update_fooditem
from schemas.request.donation import FoodItemCreate
from schemas.response.donation import FoodItemResponse
from db.dependencies import get_db
from db.models.donation import FoodItem

foodshare_router = APIRouter(
    include_in_schema=False,
    prefix='/foodshare',
    tags= ['FoodSharingPlatformWeb']
)

@foodshare_router.get("/addMyListing")
async def show_add_listing_form(request: Request) -> HTMLResponse:
    return await render_template(
        name="foodshare/addDonation.html",
        context={
            "request": request,
        },
    )

@foodshare_router.get("/myListings")
async def myListing(request: Request) -> HTMLResponse:
    return await render_template(
        name="foodshare/listMyDonations.html",
        context={
            "request": request,
        },
    )

@foodshare_router.get("/editMyListing")
async def myListing(request: Request) -> HTMLResponse:
    return await render_template(
        name="foodshare/editDonationInfo.html",
        context={
            "request": request,
        },
    )