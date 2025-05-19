# services/review_service/api/schemas.py

from pydantic import BaseModel
from datetime import datetime

# === Отзывы ===
class ReviewCreate(BaseModel):
    product_id: int
    user_id: int
    text: str

class ReviewOut(BaseModel):
    id: int
    product_id: int
    user_id: int
    text: str
    sentiment: str
    pos_score: float
    neg_score: float
    created_at: datetime

    class Config:
        orm_mode = True


# === Рекомендации ===
class RecommendationOut(BaseModel):
    id: int
    user_id: int
    product_id: int
    score: float
    recommended_at: datetime

    class Config:
        from_attributes = True


# === Поисковый запрос и вывод ===
class QueryRequest(BaseModel):
    query: str

class ProductOut(BaseModel):
    id: int
    name: str
    sentiment_score: float
    pos_percent: float
