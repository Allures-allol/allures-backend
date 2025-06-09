# models/discount.py
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean
from common.db.base import Base

class Discount(Base):
    __tablename__ = "discounts"

    id = Column(Integer, primary_key=True)
    code = Column(String(50), unique=True, index=True, nullable=False)
    percentage = Column(Float, nullable=False)
    active = Column(Boolean, default=True)
    valid_until = Column(DateTime)
