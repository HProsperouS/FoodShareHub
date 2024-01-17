# # db/crud/donation_crud.py
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from db.models.donation import Donation,FoodItem,FoodItemCategory


async def search_donation_by_category(db: Session, category: str):
    return (
        db.query(Donation)
        .join(Donation.FoodItem)  # Join to FoodItem
        .join(FoodItem.Category)  # Join to Category
        .where(
            and_(
                Donation.Status != "INACTIVE",
                func.lower(FoodItemCategory.Name).contains(category)
            )
        )
        .order_by(Donation.CreatedDate.desc())
        .all()
    )
    

async def search_donation_by_name(db: Session, name: str):
    return (
        db.query(Donation)
        .join(Donation.FoodItem)  # Join to FoodItem
        .where(
            and_(
                Donation.Status != "INACTIVE",
                func.lower(FoodItem.Name).contains(name)
            )
        )
        .order_by(Donation.CreatedDate.desc())
        .all()
    )

async def search_donation_by_category_and_name(db: Session, category:str, name: str):
    return (
        db.query(Donation)
        .join(Donation.FoodItem)  # Join to FoodItem
        .join(FoodItem.Category)  # Join to Category
        .where(
            and_(
                Donation.Status != "INACTIVE",
                func.lower(FoodItemCategory.Name).contains(category),
                func.lower(FoodItem.Name).contains(name)
            )
        )
        .order_by(Donation.CreatedDate.desc())
        .all()
    )