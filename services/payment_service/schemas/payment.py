# services/payment_service/schemas/payment.py
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from decimal import Decimal

class PaymentBase(BaseModel):
    user_id: Optional[int] = None
    subscription_id: Optional[int] = None
    amount: Decimal = Field(..., gt=0)
    status: str = "pending"
    payment_url: Optional[str] = None
    provider: Optional[str] = None
    provider_invoice_id: Optional[str] = None

class PaymentCreate(PaymentBase):
    pass

class PaymentOut(PaymentBase):
    id: int
    created_at: datetime
    class Config:
        from_attributes = True

