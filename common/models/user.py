# services/common/models/user.py
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from datetime import datetime
from common.db.base import Base
from sqlalchemy.orm import relationship

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

    # Убираем циклический импорт: описываем связь без импорта Upload и Order
    # uploads = relationship("Upload", back_populates="user", lazy="selectin")
    # sales = relationship("Sales", back_populates="user", lazy="selectin")

