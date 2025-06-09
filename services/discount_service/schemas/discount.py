# schemas/discount.py
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class DiscountCreate(BaseModel):
    code: str
    percentage: float
    valid_until: Optional[datetime] = None  # ← название как в модели

class DiscountOut(DiscountCreate):
    id: int
    active: bool  # ← не забудь, это поле тоже есть в БД

    class Config:
        from_attributes = True
