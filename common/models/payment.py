# common/models/payment.py

from sqlalchemy import Column, Integer, String, Numeric, DateTime, text
from common.db.base import Base

class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=True, index=True)           # ← без ForeignKey
    subscription_id = Column(Integer, nullable=True)               # ← без ForeignKey
    amount = Column(Numeric(10, 2), nullable=False)
    status = Column(String(20), default="pending", nullable=False)
    payment_url = Column(String(255), nullable=True)
    provider = Column(String(20), nullable=True)
    provider_invoice_id = Column(String(100), nullable=True)
    created_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"), nullable=False)

