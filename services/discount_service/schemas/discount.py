# schemas/discount.py
from pydantic import BaseModel
from datetime import datetime

class DiscountCreate(BaseModel):
    code: str
    percentage: float
    expires_at: datetime

class DiscountOut(DiscountCreate):
    id: int

    class Config:
        orm_mode = True
