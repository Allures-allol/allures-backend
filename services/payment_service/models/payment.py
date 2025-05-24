# services/payment_service/models/payment.py
from sqlalchemy import Column, Integer, String, Float, DateTime
from common.db.base import Base
from datetime import datetime

class Payment(Base):
    __tablename__ = "payments"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    amount = Column(Float)
    status = Column(String)
    payment_url = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)