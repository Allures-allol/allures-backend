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

    # Убираем циклический импорт: описываем связь без импорта Upload и Order
    # uploads = relationship("Upload", back_populates="user", lazy="selectin")
    # sales = relationship("Sales", back_populates="user", lazy="selectin")

