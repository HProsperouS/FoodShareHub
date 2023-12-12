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
    ORJSONResponse
)
from fastapi.encoders import jsonable_encoder

from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date
import os, boto3
from botocore.exceptions import ClientError 

# import local libraries
from utils.jinja2_helper import (
    flash, 
    render_template,
)
from db import (
    # DB Session
    get_db,
    # DB Query
    get_all_FoodItemCategories,
    get_all_donations,
    get_donation_by_id,
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
async def show_my_listings_page(request: Request, db: Session = Depends(get_db)) -> HTMLResponse:
    # TODO: Modify the method to get donations based on the (User ID or User Name) from the Session once Coginito Login is done
    donations = get_all_donations(db)
    count = len(donations)

    return await render_template(
        name="foodshare/listMyDonations.html",
        context={
            "request": request,
            "donations": donations,
            "count": count
        },
    )

@foodshare_router.get("/editMyListing/{id}")
async def editMyListing(request: Request, id: int, db: Session = Depends(get_db)) -> HTMLResponse:

    myDonation = await get_donation_by_id(db, id)
    categories = await get_all_FoodItemCategories(db)

    return await render_template(
        name="foodshare/editDonationInfo.html",
        context={
            "request": request,
            "donation": myDonation,
            "categories": categories
        },
    )