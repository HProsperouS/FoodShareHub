# db/crud/fooditem_crud.py
from sqlalchemy.orm import Session
from db.models.donation import FoodItem


def add_fooditem(db: Session, fooditem_data: dict):
    db_fooditem = FoodItem(**fooditem_data)
    db.add(db_fooditem)
    db.commit()
    db.refresh(db_fooditem)
    return db_fooditem

def get_all_fooditems(db: Session):
    return db.query(FoodItem).order_by(FoodItem.id).all()

def get_fooditem_by_id(db: Session, fooditem_id: int):
    return db.query(FoodItem).filter(FoodItem.id == fooditem_id).first()

def update_fooditem(db: Session, fooditem_id: int, fooditem_data: dict):
    db_fooditem = get_fooditem_by_id(db, fooditem_id)
    if db_fooditem:
        for key, value in fooditem_data.items():
            setattr(db_fooditem, key, value)
        db.commit()
        db.refresh(db_fooditem)
    return db_fooditem
