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
from pydantic import ValidationError
from sqlalchemy.orm import Session
from datetime import date
import os, boto3
from botocore.exceptions import ClientError 
import base64
import uuid
import botocore

# import local libraries
from utils.jinja2_helper import (
    flash, 
    render_template,
    url_for
)
from utils.helper import (
    decode_base64_file
)
from utils import constants as C
from db.crud.fooditem_crud import add_fooditem, get_all_fooditems, get_fooditem_by_id, update_fooditem
from schemas.request.donation import FoodItemCreate
from schemas.response.donation import FoodItemResponse
from db.dependencies import get_db
from db.models.donation import FoodItem


foodshare_api = APIRouter(
    include_in_schema=True,
    prefix=C.API_PREFIX,
    tags= ['FoodSharingPlatformAPI']
)

s3 = boto3.client('s3')
def upload_to_s3(file_data, file_name, bucket_name):
    try:
        s3 = boto3.client('s3')
        folder_path = "uploads/"
        s3.upload_fileobj(file_data, bucket_name, f"{folder_path}{file_name}")
        return True
    except botocore.exceptions.ClientError as e:
        print(f"Error uploading to S3: {e}")
        return False
    
@foodshare_api.post(
    path="/foodshare/addMyListing",
    description="Create FoodItem and list donation. ",
)
async def process_add_listing_form(request: Request, formData: FoodItemCreate, db: Session = Depends(get_db)) -> RedirectResponse:
    # try:
        
    #     return JSONResponse(content={"message": "Data received successfully"})
    # except ValidationError as e:
    #     print(e.errors())
    #     print(e.json())
    #     return JSONResponse(content={"error": str(e)}, status_code=422)

    # Process the form data
    print(f"Product Name: {formData.name}")
    print(f"Category: {formData.category}")
    print(f"Description: {formData.description}")
    print(f"Expiry Date: {formData.expiry_date}")
    print(f"Postal Code: {formData.postal_code}")
    print(f"Postal Code: {formData.image.filename}")

    # Start: Upload image to S3 
    unique_filename = str(uuid.uuid4()) + "_" + formData.image.filename
    image_data = base64.b64decode(formData.image.base64)
    file = decode_base64_file(formData.image.base64)

    # Upload the image to S3
    if upload_to_s3(file, unique_filename, C.S3_BUCKET_NAME):
        print("Image uploaded to S3 successfully")
    else:
        return JSONResponse(content={"error": "Failed to upload image to S3"}, status_code=500)

    # Start: Save FoodItem created into RDS
    # Save the form data to the database
    # db_fooditem = FoodItem(
    #     name=name,
    #     category=category,
    #     description=description,
    #     image=image,
    #     expiry_date=expiry_date,
    # )
    # db.add(db_fooditem)
    # db.commit()
    # db.refresh(db_fooditem)
    # End: Save FoodItem created into RDS

    flash(
        request=request,
        message="Your product have been uploaded successfully", 
        category="success",
    )

    # Render a response, you can customize this based on your needs
    return RedirectResponse(url="/",status_code=303)
    #return RedirectResponse(url="/", status_code=303)



