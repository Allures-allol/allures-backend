# common/models/payment.py
from sqlalchemy import Column, Integer, Numeric, String, ForeignKey, TIMESTAMP, text
from common.db.base import Base

class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    company_id = Column(Integer, nullable=True)  # добавлено
    subscription_id = Column(Integer, ForeignKey("subscriptions.id"), nullable=True)

    amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(10), server_default="UAH")  # добавлено

    status = Column(String(20), server_default="pending")   # pending / success / failed
    payment_url = Column(String(255), nullable=True)
    provider = Column(String(20), nullable=True)            # 'monobank' / 'nowpayments'
    provider_invoice_id = Column(String(100), nullable=True)

    tariff = Column(String(50), nullable=True)
    language = Column(String(10), nullable=True)
    description = Column(String, nullable=True)

    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(
        TIMESTAMP,
        server_default=text("CURRENT_TIMESTAMP"),
        server_onupdate=text("CURRENT_TIMESTAMP"),  # в SQLAlchemy для Postgres это ок как server_onupdate
    )
