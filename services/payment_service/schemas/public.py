# services/payment_service/schemas/public.py
from typing import Optional
from pydantic import BaseModel, ConfigDict
from datetime import datetime

class PaymentOut(BaseModel):
    id: int
    provider: str
    provider_invoice_id: Optional[str] = None
    status: str
    amount: float
    currency: str = "UAH"
    payment_url: Optional[str] = None
    user_id: Optional[int] = None
    company_id: Optional[int] = None
    subscription_id: Optional[int] = None
    tariff: Optional[str] = None
    language: Optional[str] = None
    description: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class OrderOut(BaseModel):
    id: int
    user_id: int
    company_id: Optional[int] = None
    product_id: Optional[int] = None
    quantity: Optional[int] = None
    total_price: float
    sold_at: datetime
