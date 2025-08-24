# common/models/payment.py
from sqlalchemy import Column, Integer, Numeric, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from common.db.base import Base

class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    subscription_id = Column(Integer, ForeignKey("subscriptions.id"), nullable=True)

    amount = Column(Numeric(10, 2), nullable=False)
    status = Column(String(20), default="pending")
    payment_url = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
