# services/common/models/user.py
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime

from common.db.base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    login = Column(String(255), unique=True, nullable=False)
    password = Column(String, nullable=False)
    full_name = Column(String(100))
    email = Column(String(255))
    phone = Column(String(30))
    avatar_url = Column(String(255))
    language = Column(String(20), default="uk")
    bonus_balance = Column(Integer, default=0)
    delivery_address = Column(String(255))
    registered_at = Column(DateTime, default=datetime.utcnow)
    role = Column(String(50), default="user")
    is_blocked = Column(Boolean, default=False)

    sales = relationship("Sales", back_populates="user", cascade="all, delete")
    uploads = relationship("Upload", back_populates="user", cascade="all, delete")
    reviews = relationship("Review", back_populates="user", cascade="all, delete-orphan")
    subscriptions = relationship("UserSubscription", back_populates="user", cascade="all, delete")


from common.models.sales import Sales
from common.models.uploads import Upload
from services.review_service.models.review import Review
