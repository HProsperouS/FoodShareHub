# import third-party libraries
from fastapi import (
    APIRouter,
    Request,
    Depends,
    Query
)
from fastapi.responses import (
    HTMLResponse,
    RedirectResponse
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
    # Search
    search_donation_by_name,
    search_donation_by_category,
    search_donation_by_category_and_name
)
from utils import constants as C
from depends import (
    rbac
)
from aws.services import(
    autocomplete_address
)

RBAC_DEPENDENCY = Depends(rbac.USER_RBAC, use_cache=False)

foodshare_router = APIRouter(
    include_in_schema=False,
    prefix='/foodshare',
    tags= ['FoodSharingPlatformWeb']
)

@foodshare_router.get("/addMyListing")
async def show_add_listing_form(request: Request, rbac_res: rbac.RBACResults | RedirectResponse = RBAC_DEPENDENCY, db:Session = Depends(get_db)) :
    # if not isinstance(rbac_res, rbac.RBACResults):
    #     print(rbac_res)
    #     return rbac_res
    
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
    session = request.session.get(C.SESSION_COOKIE, None)

    # print("Session: ",session)
    # print("Session Username",session["username"])
    # print("Session UserId",session["user_id"])

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

@foodshare_router.get("/donationDetails/{id}")
async def donationDetails(request: Request, id: int, db: Session = Depends(get_db)) -> HTMLResponse:

    myDonation = await get_donation_by_id(db, id)

    return await render_template(
        name="foodshare/donationDetails.html",
        context={
            "request": request,
            "donation": myDonation,
        },
    )

@foodshare_router.get(
    path="/search",
    description="search for food items avaliable on food share hub",
)
async def process_search(
    request: Request,
    category: str = Query(None, description="Search based on food item category", alias="category"),
    name: str = Query(None, description="Search based on food item name", alias="name"),
    db: Session = Depends(get_db)) -> HTMLResponse:

    # Convert to lowercase
    category_lower = category.lower() if category else None
    name_lower = name.lower() if name else None

    if name_lower is None:
        donations = await search_donation_by_category(db, category_lower)
    elif category == "All Categories":
        donations = await search_donation_by_name(db, name_lower)
    else:
        donations = await search_donation_by_category_and_name(db, category_lower, name_lower)
    
    count = len(donations)

    return await render_template(
        name="foodshare/searchResult.html",
        context={
            "request": request,
            "donations": donations, 
            "count": count
        },
    )

@foodshare_router.get(
    path="/autocomplete/{query}",
    description="Address suggestions based on the input",
)
async def get_autocomplete_results(query: str):
    results = autocomplete_address(query)
    if results:
        return {"suggestions": results}
    else:
        return {"message": "No suggestion found!"}
