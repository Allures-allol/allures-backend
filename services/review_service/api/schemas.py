import strawberry
from datetime import datetime
from sqlalchemy.orm import Session
from common.db.session import SessionLocal
from common.models.products import Product as ProductModel
from services.review_service.models.review import Review as ReviewModel
from services.review_service.models.recommendation import Recommendation as RecommendationModel
from pydantic import BaseModel
from datetime import datetime, date, timedelta
from typing import Optional

class ReviewCreate(BaseModel):
    product_id: int
    user_id: int
    text: str
    sentiment: Optional[str] = None  # если определяется ИИ
    pos_score: Optional[float] = None
    neg_score: Optional[float] = None

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
        from_attributes = True

# === Рекомендации ===
class RecommendationOut(BaseModel):
    id: int
    user_id: int
    product_id: int
    score: float
    recommended_at: Optional[datetime] = None

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
