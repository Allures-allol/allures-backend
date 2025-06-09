from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from common.db.base import Base
from datetime import datetime

class Payment(Base):
    __tablename__ = "payments"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    amount = Column(Float, nullable=False)
    status = Column(String(20), default="pending")
    payment_url = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)


