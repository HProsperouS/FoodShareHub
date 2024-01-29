from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from enum import Enum as PythonEnum
from datetime import datetime
from db.base import Base
from utils.helper import get_current_time_in_singapore

'''SQLAlchemy models'''
class FoodItemCategory(Base):
    __tablename__ = "FoodItemCategories"

    Id = Column(Integer, primary_key=True, index=True)
    Name = Column(String, default="")

    FoodItems = relationship("FoodItem", back_populates="Category")

    def to_json_serializable(self):
        return {
            'Name': self.Name,
        }

class Attachment(Base):
    __tablename__ = "Attachments"

    Id = Column(Integer, primary_key=True, index=True)
    FileName = Column(String, default="")
    ContentType = Column(String, default="")
    FileSize = Column(Integer, default="")
    FilePath = Column(String, default="")
    PublicAccessURL = Column(String, default="")
    FoodItem = relationship("FoodItem", back_populates="Attachment")
    
    def to_json_serializable(self):
        return {
            'PublicAccessURL': self.PublicAccessURL,
        }

class FoodItem(Base):
    __tablename__ = "FoodItems"

    Id = Column(Integer, primary_key=True, index=True)
    Name = Column(String, default="")
    Description = Column(String, default="")
    
    CategoryID = Column(Integer, ForeignKey("FoodItemCategories.Id"))
    Category = relationship("FoodItemCategory", back_populates="FoodItems")

    ExpiryDate = Column(DateTime)

    AttachmentID = Column(Integer, ForeignKey("Attachments.Id"))
    Attachment = relationship("Attachment", back_populates="FoodItem", cascade="save-update, merge")
    Donation = relationship("Donation", back_populates="FoodItem")
    
    def to_json_serializable(self):
        return {
            'Id': self.Id,
            'Name': self.Name,
            'Description': self.Description,
            'Category': self.Category.to_json_serializable(),  
            'Attachment': self.Attachment.to_json_serializable() if self.Attachment else None, 
        }

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
    CreatedDate = Column(DateTime, default=datetime.now)
    UpdatedDate = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    # End: Set the timezone to Singapore

    MeetUpLocation = Column(String, default="")
    
    UserId = Column(String, default="")
    Username = Column(String, default="Liu JiaJun")

    # Relationships
    FoodItemID = Column(Integer, ForeignKey("FoodItems.Id"))
    FoodItem = relationship("FoodItem", back_populates="Donation", cascade="save-update, merge")

    def to_json_serializable(self):
        return {
            'Username': self.Username,
            'Status': self.Status.value,  
            'CreatedDate': self.CreatedDate.isoformat(),
            'MeetUpLocation': self.MeetUpLocation,
            'FoodItem': self.FoodItem.to_json_serializable(), 
        }

