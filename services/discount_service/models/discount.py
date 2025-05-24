# models/discount.py
from sqlalchemy import Column, Integer, String, Float, DateTime
from common.db.base import Base
from datetime import datetime

class Discount(Base):
    __tablename__ = "discounts"
    id = Column(Integer, primary_key=True)
    code = Column(String, unique=True, index=True)
    percentage = Column(Float)
    expires_at = Column(DateTime)
