from sqlalchemy import Column, Integer, String, DateTime, Boolean
from datetime import datetime
from common.db.base import Base

class AdminUser(Base):
    __tablename__ = "admin"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    subscription_status = Column(Boolean, default=False)
