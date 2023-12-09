# import third-party libraries
from fastapi import (
    APIRouter,
    Request,
    Depends,
)
from fastapi.responses import (
    ORJSONResponse
)
from pydantic import ValidationError
from sqlalchemy.orm import Session

# import local libraries
from utils.jinja2_helper import (
    flash, 
)
from utils.helper import (
    decode_base64_file
)
from utils import constants as C
from db import (
    # FoodItem Section
    add_fooditem, 
    get_all_fooditems, 
    get_fooditem_by_id, 
    update_fooditem,
    # Donation Section
    add_donation
)
from schemas.request.donation import FoodItemCreate
from schemas.response.donation import FoodItemResponse
from db.dependencies import get_db

from db.models.donation import (
    FoodItem, 
    Attachment,
    Donation,
    DonationStatus
)

from aws.services import(
    upload_to_s3
)

# import Python's standard libraries
from datetime import datetime
import uuid

foodshare_api = APIRouter(
    include_in_schema=True,
    prefix=C.API_PREFIX,
    tags= ['FoodSharingPlatformAPI']
)

@foodshare_api.post(
    path="/foodshare/addMyListing",
    description="Create FoodItem and list donation. ",
)
async def process_add_listing_form(request: Request, formData: FoodItemCreate, db: Session = Depends(get_db)) -> ORJSONResponse:
    # try:
        
    #     return ORJSONResponse(content={"message": "Data received successfully"})
    # except ValidationError as e:
    #     print(e.errors())
    #     print(e.json())
    #     return ORJSONResponse(content={"error": str(e)}, status_code=422)

    # Start: Upload image to S3 
    unique_filename = str(uuid.uuid4()) + "_" + formData.Image.FileName
    file = decode_base64_file(formData.Image.Base64)

    if upload_to_s3(file, unique_filename, C.S3_BUCKET_NAME, formData.Image.ContentType):
        print("Image uploaded to S3 successfully")
    else:
        return ORJSONResponse(content={"error": "Failed to upload image to S3"}, status_code=500)
    # End: Upload image to S3 

    # Start: Save FoodItem and Attachment into RDS using cascading
    s3_file_path = f"s3://{C.S3_BUCKET_NAME}/uploads/{unique_filename}"

    #Sample of the URL: https://myfoodsharehub-bucket.s3.amazonaws.com/uploads/997941e7-8a79-4fd7-a103-ed338fdf9a7f_logo.svg
    publicAccessURL = f"https://{C.S3_BUCKET_NAME}.s3.amazonaws.com/uploads/{unique_filename}"
    new_attachment = Attachment(
        FileName=unique_filename,
        ContentType=formData.Image.ContentType,
        FileSize=formData.Image.Size,
        FilePath=s3_file_path,
        PublicAccessURL = publicAccessURL
    )

    new_fooditem = FoodItem(
        Name=formData.Name,
        Description=formData.Description,
        CategoryID=formData.CategoryID,
        Attachment=new_attachment
    )

    new_donation = Donation(
        Status=DonationStatus.ACTIVE,
        CreatedDate=datetime.now(),
        MeetUpLocation=formData.PostalCode,
        Username = "JiaJun Liu",
        FoodItem = new_fooditem
    )

    add_donation(db, new_donation)
    # End: Save FoodItem and Attachment into RDS using cascading

    # Flash Message TOBE shown in the redirected page
    flash(
        request=request,
        message="Your product have been uploaded successfully", 
        category="success",
    )

    # Redirect URL in the JSON response
    redirect_url = "/"

    return ORJSONResponse(
        content={"redirect_url": redirect_url}
    )




