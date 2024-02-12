# import third-party libraries
from fastapi import (
    APIRouter,
    Request,
    Depends,
    Query,
    HTTPException, 
    status
)
from fastapi.responses import (
    ORJSONResponse
)
from pydantic import ValidationError
from sqlalchemy.orm import Session

# import local libraries
from utils.helper import (
    decode_base64_file
)
from utils import constants as C
from utils import helper as Helper
from db import (
    # FoodItem Section
    add_fooditem, 
    get_all_fooditems, 
    get_fooditem_by_id, 
    update_fooditem,
    # Donation Section
    add_donation,
    update_donation,
    softdelete_donation,
    update_donation_status,
    # Search
    search_donation_by_name,
    search_donation_by_category
)
from schemas.request.donation import (
    DonationCreate, 
    DonationUpdate, 
    ImageData, 
    DonationData, 
    DonationEditStatus
)
from db.dependencies import get_db

from db.models.donation import (
    FoodItem, 
    Attachment,
    Donation,
    DonationStatus
)

from aws.services import(
    upload_to_s3,
    detect_objects,
    detect_objects_and_moderate,
    analyze_comprehend_toxicity
)

# import Python's standard libraries
from datetime import datetime
import uuid
import base64

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
    # Get user_id and username from session
    session = request.session.get(C.SESSION_COOKIE, None)
    user_id = session["user_id"]
    username = session["username"]

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
        MeetUpLocation=formData.MeetUpLocation,
        UserId = user_id,
        Username = username,
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


@foodshare_api.post(
    path="/foodshare/detectobject",
    description="Detect FoodItem Image uploaded and return labels",
)
async def detect_fooditem(image_data: ImageData):
    image_bytes = base64.b64decode(image_data.base64_data)
    labels, inappropriate_labels = detect_objects_and_moderate(image_bytes)
    # print(labels)
    # print(inappropriate_labels)
    if inappropriate_labels:
        return ORJSONResponse(content={"message": "Inappropriate content detected. Please upload another image to avoid a ban."})
    else:
        return ORJSONResponse(content={"labels": labels})
    
@foodshare_api.post(
    path="/foodshare/deleteMyListing/{id}",
    description="Soft delete listings, set the status of the donation to INACTIVE based on the donation id",
)
async def process_delete_listing(id: int, db: Session = Depends(get_db)) -> ORJSONResponse:

    # # Set the donation status to INACTIVE
    await softdelete_donation(db, id)

    # Toastr 
    success_message = {"category": "success", "text": "Your product have been deleted successfully"}

    # Redirect URL in the JSON response
    redirect_url = "/foodshare/myListings"

    return ORJSONResponse(
        content={"redirect_url": redirect_url, "message": success_message}
    )

@foodshare_api.post(
    path="/foodshare/detect_toxicity",
    description="Detect food item name and description for toxicity.",
)
async def detect_toxicity(text: DonationData):
    
    hasToxicWords = analyze_comprehend_toxicity(text.Name + " " + text.Description)
    
    print("Words For detect_toxicity ", text)
    print("hasToxicWords", hasToxicWords)
    
    if hasToxicWords:
        return ORJSONResponse(content={"isToxic": hasToxicWords ,"message": "Inappropriate language detected. Please mind your langueage."})
    else:
        return ORJSONResponse(content={"isToxic": hasToxicWords})
    

@foodshare_api.post(
    path="/foodshare/editListingStatus",
    description="Edit Donation Listing Status",
)
async def process_edit_status_form(request: Request, formData: DonationEditStatus, db: Session = Depends(get_db)) -> ORJSONResponse:

    await update_donation_status(db, formData.id, formData.donationStatus)
    success_message = {"category": "success", "text": "Your Listing Status have been edited successfully"}
    redirect_url = "/foodshare/myListings"

    return ORJSONResponse(
        content={"redirect_url": redirect_url, "message":success_message}
    )