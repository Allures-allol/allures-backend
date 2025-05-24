# services/common/models/user.py
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from common.db.base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    login = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    registered_at = Column(DateTime, default=datetime.utcnow)
    role = Column(String, default="user")
    is_blocked = Column(Boolean, default=False)

    # Пример связей:
    # uploads = relationship("Upload", back_populates="user")
    # orders = relationship("Order", back_populates="user")
