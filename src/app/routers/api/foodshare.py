# import third-party libraries
from fastapi import (
    APIRouter,
    Request,
    Depends,
    HTTPException, 
    status
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
    add_donation,
    update_donation
)
from schemas.request.donation import DonationCreate, DonationUpdate
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
async def process_add_listing_form(request: Request, formData: DonationCreate, db: Session = Depends(get_db)) -> ORJSONResponse:
    # Start: Upload image to S3 
    unique_filename = str(uuid.uuid4()) + "_" + formData.FoodItem.Image.FileName
    file = decode_base64_file(formData.FoodItem.Image.Base64)

    if upload_to_s3(file, unique_filename, C.S3_BUCKET_NAME, formData.FoodItem.Image.ContentType):
        print("Image uploaded to S3 successfully")
    else:
        return ORJSONResponse(content={"error": "Failed to upload image to S3"}, status_code=500)
    # End: Upload image to S3 

    # Start: Save FoodItem and Attachment into RDS using cascading
    s3_file_path = f"s3://{C.S3_BUCKET_NAME}/uploads/{unique_filename}"
    publicAccessURL = f"https://{C.S3_BUCKET_NAME}.s3.amazonaws.com/uploads/{unique_filename}"

    new_attachment = Attachment(
        FileName=unique_filename,
        ContentType=formData.FoodItem.Image.ContentType,
        FileSize=formData.FoodItem.Image.Size,
        FilePath=s3_file_path,
        PublicAccessURL = publicAccessURL
    )

    new_fooditem = FoodItem(
        Name=formData.FoodItem.Name,
        Description=formData.FoodItem.Description,
        ExpiryDate=formData.FoodItem.ExpiryDate,
        CategoryID=formData.FoodItem.CategoryID,
        Attachment=new_attachment,
    )

    new_donation = Donation(
        Status=DonationStatus.ACTIVE,
        CreatedDate=datetime.now(),
        MeetUpLocation=formData.MeetUpLocation,
        Username = "JiaJun Liu",
        FoodItem = new_fooditem
    )

    add_donation(db, new_donation)
    # End: Save FoodItem and Attachment into RDS using cascading

    # Toastr TOBE shown in the redirected page
    success_message = {"category": "success", "text": "Your product have been added successfully"}

    # Redirect URL in the JSON response
    redirect_url = "/"

    return ORJSONResponse(
        content={"redirect_url": redirect_url, "message":success_message}
    )

@foodshare_api.post(
    path="/foodshare/editMyListing/{donation_id}",
    description="Edit donation details. ",
)
async def process_update_listing_form(
    request: Request,
    donation_id: int,
    formData: DonationUpdate,
    db: Session = Depends(get_db),
) -> ORJSONResponse:
    # Check if the image is updated
    image_updated = formData.FoodItem.Image.Uploaded

     # Start: Upload image to S3， Upload to S3 if the image being updated
    if(image_updated):
        unique_filename = str(uuid.uuid4()) + "_" + formData.FoodItem.Image.FileName
        file = decode_base64_file(formData.FoodItem.Image.Base64)

        if upload_to_s3(file, unique_filename, C.S3_BUCKET_NAME, formData.FoodItem.Image.ContentType):
            print("Image uploaded to S3 successfully")
        else:
            return ORJSONResponse(content={"error": "Failed to upload image to S3"}, status_code=500)
    # End: Upload image to S3, Upload to S3 if the image being updated
    
    # Start: Create Attachment if the image is updated
    if image_updated:
        s3_file_path = f"s3://{C.S3_BUCKET_NAME}/uploads/{unique_filename}"
        public_access_url = f"https://{C.S3_BUCKET_NAME}.s3.amazonaws.com/uploads/{unique_filename}"

        updated_attachment = Attachment(
            FileName=unique_filename,
            ContentType=formData.FoodItem.Image.ContentType,
            FileSize=formData.FoodItem.Image.Size,
            FilePath=s3_file_path,
            PublicAccessURL=public_access_url
        )
    else:
        updated_attachment = None
    # End: Create Attachment
    
    # Create updated FoodItem
    updated_food_item = FoodItem(
        Name=formData.FoodItem.Name,
        Description=formData.FoodItem.Description,
        ExpiryDate=formData.FoodItem.ExpiryDate,
        CategoryID=formData.FoodItem.CategoryID,
        Attachment=updated_attachment
    )

    # Create updated Donation
    updated_donation = Donation(
        Status=DonationStatus.ACTIVE,
        MeetUpLocation=formData.MeetUpLocation,
        Username="JiaJun Liu",
        UpdatedDate=datetime.now(),
        FoodItem=updated_food_item
    )

    # Save updated Donation to the database
    await update_donation(db, donation_id, updated_donation, image_updated)

    # Toastr TOBE shown in the redirected page
    success_message = {"category": "success", "text": "Your product have been updated successfully"}

    # Redirect URL in the JSON response
    redirect_url = "/"

    return ORJSONResponse(
        content={"redirect_url": redirect_url, "message": success_message}
    )
    