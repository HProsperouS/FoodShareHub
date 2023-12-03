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
from db import (
    get_all_FoodItemCategories,
    get_db,
)

foodshare_router = APIRouter(
    include_in_schema=False,
    prefix='/foodshare',
    tags= ['FoodSharingPlatformWeb']
)

@foodshare_router.get("/addMyListing")
async def show_add_listing_form(request: Request, db: Session = Depends(get_db) ) -> HTMLResponse:
    categories = await get_all_FoodItemCategories(db)
    return await render_template(
        name="foodshare/addDonation.html",
        context={
            "request": request,
            "categories": categories,  # Pass the categories to the DDL
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