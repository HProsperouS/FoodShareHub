# db/crud/fooditem_crud.py
from sqlalchemy.orm import Session
from db.models.donation import FoodItemCategory

async def get_all_FoodItemCategories(db: Session):
    return db.query(FoodItemCategory).order_by(FoodItemCategory.Id).all()