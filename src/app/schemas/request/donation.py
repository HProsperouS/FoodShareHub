# schemas/request/donation.py
from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional
from ..enums import DonationStatus
from fastapi import UploadFile


class AttachmentCreate(BaseModel):
    filename: str
    content_type: str
    size: int
    base64: str

class FoodItemCreate(BaseModel):
    name: str
    category: str
    description: str
    expiry_date: date
    postal_code: Optional[str] = None
    image: AttachmentCreate

class DonationCreate(BaseModel):
    status: DonationStatus
    location: str = ''
    fooditem: FoodItemCreate
