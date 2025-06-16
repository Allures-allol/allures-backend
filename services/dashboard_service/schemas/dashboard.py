#services/dashboard_service/schemas/dashboard.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


# 📊 Dashboard общая информация
class DashboardOut(BaseModel):
    id: int
    full_name: Optional[str]
    email: str
    phone: Optional[str]
    avatar_url: Optional[str]
    language: Optional[str]
    bonus_balance: Optional[int]
    delivery_address: Optional[str]
    sales_count: int
    reviews_count: int
    discounts_count: int

    class Config:
        from_attributes = True

# ✅ Продажа (Sales)
class Sale(BaseModel):
    id: int
    product_id: int
    category_id: int
    user_id: int
    quantity: int
    sold_at: datetime
    total_price: float
    revenue: float

    class Config:
        from_attributes = True

# ✅ Отзыв (Review)
class Review(BaseModel):
    id: int
    product_id: int
    user_id: int
    text: str
    sentiment: str
    pos_score: float
    neg_score: float
    created_at: datetime

    class Config:
        from_attributes = True

# ✅ Скидка (Discount)
class Discount(BaseModel):
    id: int
    code: str
    percentage: float
    active: bool
    valid_until: Optional[datetime]  # допускаем null

    class Config:
        from_attributes = True

# ✅ Рекомендация (Recommendation)
class Recommendation(BaseModel):
    id: int
    user_id: int
    product_id: int
    score: float
    recommended_at: Optional[datetime]

    class Config:
        from_attributes = True

