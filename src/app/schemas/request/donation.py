# schemas/request/donation.py
from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional
from ..enums import DonationStatus
from fastapi import UploadFile


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
    PostalCode: Optional[str] = None
    Image: AttachmentCreate

class DonationCreate(BaseModel):
    Status: DonationStatus
    Location: str = ''
    FoodItem: FoodItemCreate
