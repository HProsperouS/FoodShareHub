from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from enum import Enum as PythonEnum
from datetime import datetime
from db.base import Base


'''SQLAlchemy models'''
class FoodItemCategory(Base):
    __tablename__ = "food_item_categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, default="")
    food_items = relationship("FoodItem", back_populates="category")

class FoodItem(Base):
    __tablename__ = "food_items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, default="")
    description = Column(String, default="")
    category_id = Column(Integer, ForeignKey("food_item_categories.id"))

    category = relationship("FoodItemCategory", back_populates="food_items")

class DonationStatus(PythonEnum):
    ACTIVE = 'ACTIVE'
    RESERVED = 'RESERVED'
    COMPLETED = 'COMPLETED'
    CANCELLED = 'CANCELLED'

class Donation(Base):
    __tablename__ = "donations"

    id = Column(Integer, primary_key=True, index=True)
    status = Column(Enum(DonationStatus), nullable=False)
    date = Column(DateTime, default=datetime.now)
    location = Column(String, default="")

    # user_id = Column(Integer, ForeignKey("users.id"))
    # user = relationship("User", back_populates="donations")
    @property
    def donor(self):
        # Use AWS Cognito APIs to fetch user details based on cognito_sub
        # Example: Use Boto3 to call Cognito APIs
        # user_details = cognito_client.admin_get_user(UserPoolId='your_user_pool_id', Username=self.cognito_sub)
        # return user_details['Username']
        pass
    
    food_item_id = Column(Integer, ForeignKey("food_items.id"))
    food_item = relationship("FoodItem", back_populates="donation")
    donation_request = relationship("DonationRequest", back_populates="donation")

class RequestStatus(PythonEnum):
    PENDING = 'PENDING'
    ACCEPTED = 'ACCEPTED'
    DONE = 'DONE'

class DonationRequest(Base):
    __tablename__ = "donation_requests"

    id = Column(Integer, primary_key=True, index=True)
    donation_id = Column(Integer, ForeignKey("donations.id"))
    donation = relationship("Donation", back_populates="donation_request")

    # donor_id = Column(Integer, ForeignKey("users.id"))
    # donor = relationship("User", foreign_keys=[donor_id], back_populates="donation_requests_donor")

    # recipient_id = Column(Integer, ForeignKey("users.id"))
    # recipient = relationship("User", foreign_keys=[recipient_id], back_populates="donation_requests_recipient")

    @property
    def donor(self):
        # Use AWS Cognito APIs to fetch user details based on cognito_sub
        # Example: Use Boto3 to call Cognito APIs
        # user_details = cognito_client.admin_get_user(UserPoolId='your_user_pool_id', Username=self.cognito_sub)
        # return user_details['Username']
        pass

    @property
    def recipient(self):
        # Similar to the donor property, fetch recipient details
        pass

    status = Column(Enum(RequestStatus), nullable=False)
    date = Column(DateTime, default=datetime.now)


