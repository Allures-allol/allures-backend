# services.payment_service/schemas/payment.py
from pydantic import BaseModel
from datetime import datetime

class PaymentCreate(BaseModel):
    user_id: int
    amount: float
    status: str
    payment_url: str | None = None  # делаем опциональным для простоты

class PaymentOut(PaymentCreate):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True  # Pydantic v2+
