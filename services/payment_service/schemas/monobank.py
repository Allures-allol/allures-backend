# services/payment_service/schemas/monobank.py
# services/payment_service/schemas/monobank.py
from typing import Optional
from pydantic import BaseModel, Field

class MonoCreateInvoiceIn(BaseModel):
    amount_uah: float = Field(..., gt=0)
    order_id: str = Field(..., min_length=1)
    email: Optional[str] = None
    display_type: str = "iframe"
    user_id: Optional[int] = None
    subscription_id: Optional[int] = None     # ← добавили
    tariff: Optional[str] = None
    language: Optional[str] = None
    description: Optional[str] = None

class MonoCreateInvoiceOut(BaseModel):
    pageUrl: str
    invoiceId: str
    status: str = "pending"
    amount: float
    user_id: Optional[int] = None
    subscription_id: Optional[int] = None     # ← добавили
