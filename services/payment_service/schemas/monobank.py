# services/payment_service/schemas/monobank.py
from typing import Optional
from pydantic import BaseModel, Field

class MonoCreateInvoiceIn(BaseModel):
    amount_uah: float = Field(..., gt=0)
    order_id: Optional[str] = None
    email: Optional[str] = None
    display_type: str = "iframe"

    user_id: int
    company_id: Optional[int] = None
    subscription_id: Optional[int] = None

    currency: str = "UAH"
    tariff: Optional[str] = None
    language: Optional[str] = None
    description: Optional[str] = None


class MonoCreateInvoiceOut(BaseModel):
    pageUrl: str
    invoiceId: str
    status: str = "pending"
    amount: float
    currency: str = "UAH"

    user_id: Optional[int] = None
    company_id: Optional[int] = None
    subscription_id: Optional[int] = None
    subscription_code: Optional[str] = None
    subscription_name: Optional[str] = None

    tariff: Optional[str] = None
    language: Optional[str] = None
    description: Optional[str] = None
