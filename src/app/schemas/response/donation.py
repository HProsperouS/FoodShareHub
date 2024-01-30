# schemas/response/donation.py
from pydantic import BaseModel
from datetime import datetime
from ..enums import DonationStatus
from .category import CategoryResponse

class FoodItemResponse(BaseModel):
    id: int
    name: str 
    category: CategoryResponse 
    description: str 
    image: str 
    expiry_date: datetime

class DonationResponse(BaseModel):
    id: int
    status: DonationStatus
    date: datetime
    location: str = ''
    fooditem: FoodItemResponse