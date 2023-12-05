from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from enum import Enum as PythonEnum
from datetime import datetime
from db.base import Base
import pytz

'''SQLAlchemy models'''
class FoodItemCategory(Base):
    __tablename__ = "FoodItemCategories"

    Id = Column(Integer, primary_key=True, index=True)
    Name = Column(String, default="")

    FoodItems = relationship("FoodItem", back_populates="Category")

class Attachment(Base):
    __tablename__ = "Attachments"

    Id = Column(Integer, primary_key=True, index=True)
    FileName = Column(String, default="")
    ContentType = Column(String, default="")
    FileSize = Column(Integer, default="")
    FilePath = Column(String, default="")
    
    FoodItem = relationship("FoodItem", back_populates="Attachment")

class FoodItem(Base):
    __tablename__ = "FoodItems"

    Id = Column(Integer, primary_key=True, index=True)
    Name = Column(String, default="")
    Description = Column(String, default="")
    
    CategoryID = Column(Integer, ForeignKey("FoodItemCategories.Id"))
    Category = relationship("FoodItemCategory", back_populates="FoodItems")

    # attachment = relationship("Attachment", back_populates="food_item", cascade="all, delete-orphan")
    AttachmentID = Column(Integer, ForeignKey("Attachments.Id"))
    Attachment = relationship("Attachment", back_populates="FoodItem", cascade="save-update, merge")
    Donation = relationship("Donation", back_populates="FoodItem")
    
class DonationStatus(PythonEnum):
    ACTIVE = 'ACTIVE'
    INACTIVE = 'INACTIVE'
    RESERVED = 'RESERVED'
    COMPLETED = 'COMPLETED'

class Donation(Base):
    __tablename__ = "Donations"

    Id = Column(Integer, primary_key=True, index=True)
    Status = Column(Enum(DonationStatus), nullable=False)

    # Start: Set the timezone to Singapore
    singapore_timezone = pytz.timezone('Asia/Singapore')
    current_time_singapore = datetime.now(singapore_timezone)
    CreatedDate = Column(DateTime(timezone=True), default=current_time_singapore)
    # End: Set the timezone to Singapore

    MeetUpLocation = Column(String, default="")
    
    # TODO: User, TOBE Replace by Cognito Method Soon
    Username = Column(String, default="Liu JiaJun")

    # Relationships
    FoodItemID = Column(Integer, ForeignKey("FoodItems.Id"))
    FoodItem = relationship("FoodItem", back_populates="Donation", cascade="save-update, merge")



