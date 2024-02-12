# schemas/request/donation.py
from pydantic import BaseModel
from datetime import date
from typing import Optional
from ..enums import DonationStatus

class AttachmentCreate(BaseModel):
    FileName: str
    ContentType: str
    Size: int
    Base64: str

class FoodItemCreate(BaseModel):
    Name: str
    CategoryID: int
    Description: str
    ExpiryDate: date
    Image: AttachmentCreate

class DonationCreate(BaseModel):
    MeetUpLocation: str = ''
    FoodItem: FoodItemCreate

class AttachmentUpdate(BaseModel):
    FileName: str
    ContentType: str
    Size: int
    Base64: str
    Uploaded: bool

class FoodItemUpdate(BaseModel):
    Name: str
    CategoryID: int
    Description: str
    ExpiryDate: date
    PostalCode: Optional[str] = None
    Image: AttachmentUpdate

class DonationUpdate(BaseModel):
    MeetUpLocation: str = ''
    FoodItem: FoodItemUpdate

class ImageData(BaseModel):
    base64_data: str

class DonationData(BaseModel):
    Name: str
    Description: str

class DonationEditStatus(BaseModel):
    id : int 
    donationStatus : DonationStatus