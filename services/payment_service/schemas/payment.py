from pydantic import BaseModel
from datetime import datetime

class PaymentCreate(BaseModel):
    user_id: int
    amount: float
    status: str
    payment_url: str

class PaymentOut(PaymentCreate):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
