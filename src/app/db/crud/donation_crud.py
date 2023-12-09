# # db/crud/donation_crud.py
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from db.models.donation import Donation
from sqlalchemy.future import select

def add_donation(db: Session, donation_data: Donation):
    db.add(donation_data)
    db.commit()
    return donation_data

def get_all_donations(db: Session):
    return db.query(Donation).order_by(Donation.Id).all()

def get_donation_by_id(db: Session, donation_id: int):
    return db.query(Donation).filter(Donation.Id == donation_id).first()

async def update_donation(db: Session, donation_data: Donation):
    async with db.begin():
        updated_donation = await db.merge(donation_data)
        await db.commit()

    return updated_donation
