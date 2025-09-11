# --- Cart / Orders ---
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from decimal import Decimal

class CartItemIn(BaseModel):
    product_id: int
    qty: int

class CartItemOut(BaseModel):
    product_id: int
    qty: int
    price_snapshot: Decimal
    name: Optional[str] = None
    image: Optional[str] = None

class CartOut(BaseModel):
    id: int
    user_id: int
    status: str
    items: List[CartItemOut]
    updated_at: datetime

class OrderItemOut(BaseModel):
    product_id: int
    qty: int
    price_snapshot: Decimal
    name: Optional[str] = None
    image: Optional[str] = None

class OrderOut(BaseModel):
    id: int
    user_id: int
    status: str
    total_amount: Decimal
    created_at: datetime
    items: List[OrderItemOut]
