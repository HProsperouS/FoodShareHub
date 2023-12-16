# # db/crud/donation_crud.py
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from db.models.donation import Donation
from sqlalchemy.future import select

def add_donation(db: Session, donation_data: Donation):
    db.add(donation_data)
    db.commit()

def get_all_donations(db: Session):
    return db.query(Donation).order_by(Donation.Id).all()

async def get_donation_by_id(db: Session, donation_id: int):
    return db.query(Donation).filter(Donation.Id == donation_id).first()

async def update_donation(db: Session, donation_id: int, updated_data: Donation, updated_image: bool):

    # Use merge() Method to update db, This is easier to use but not good for performance as it updated every columns
    # updated_donation = db.merge(updated_data)

    existing_donation = db.query(Donation).filter_by(Id=donation_id).first()

    if existing_donation:
        # Start: FoodItem Table
        existing_donation.FoodItem.Name = updated_data.FoodItem.Name
        existing_donation.FoodItem.Description = updated_data.FoodItem.Description
        existing_donation.FoodItem.CategoryID = updated_data.FoodItem.CategoryID
        existing_donation.FoodItem.ExpiryDate = updated_data.FoodItem.ExpiryDate
        # End: FoodItem Table

        # Start: Attachment Table
        if(updated_image):
            existing_donation.FoodItem.Attachment.FileName = updated_data.FoodItem.Attachment.FileName
            existing_donation.FoodItem.Attachment.ContentType = updated_data.FoodItem.Attachment.ContentType
            existing_donation.FoodItem.Attachment.FileSize = updated_data.FoodItem.Attachment.FileSize
            existing_donation.FoodItem.Attachment.FilePath = updated_data.FoodItem.Attachment.FilePath
            existing_donation.FoodItem.Attachment.PublicAccessURL = updated_data.FoodItem.Attachment.PublicAccessURL
        # End: Attachment Table
        
        # Start: Donation Table
        existing_donation.MeetUpLocation = updated_data.MeetUpLocation
        existing_donation.UpdatedDate = updated_data.UpdatedDate
        # Start: Donation Table

        db.commit()
    else:
        print("Donation record not found.")
