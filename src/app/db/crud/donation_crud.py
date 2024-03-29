# # db/crud/donation_crud.py
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from db.models.donation import Donation
from sqlalchemy.future import select

def add_donation(db: Session, donation_data: Donation):
    db.add(donation_data)
    db.commit()

def get_all_donations(db: Session):
    # Get all donations with status not INACTIVE
    return db.query(Donation).filter(Donation.Status != "INACTIVE").order_by(Donation.Id).all()

def get_all_donations_by_userid(db: Session, user_id: str):
    # Get all donations with status not INACTIVE and user_id = user_id
    return db.query(Donation).filter(Donation.Status != "INACTIVE", Donation.UserId == user_id).order_by(Donation.Id).all()

def get_all_donations_exclude_userid(db: Session, user_id: str):
    # Get all donations with status not INACTIVE and user_id = user_id
    return db.query(Donation).filter(Donation.Status != "INACTIVE", Donation.UserId != user_id).order_by(Donation.Id).all()

async def get_donation_by_id(db: Session, donation_id: int):
    return db.query(Donation).filter(Donation.Id == donation_id).first()

async def update_donation(db: Session, donation_id: int, updated_data: Donation, updated_image: bool):
    
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

async def softdelete_donation(db: Session, donation_id: int):

    existing_donation = db.query(Donation).filter_by(Id=donation_id).first()

    if existing_donation:
        existing_donation.Status = "INACTIVE"
        db.commit()
    else:
        print("Donation record not found.")


async def update_donation_status(db: Session, donation_id: int, status: str):
    existing_donation = db.query(Donation).filter_by(Id=donation_id).first()

    if existing_donation:
        existing_donation.Status = status
        db.commit()
    else:
        print("Donation record not found.")