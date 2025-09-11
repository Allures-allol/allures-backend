# services/review_service/api/schemas.py
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field

# --- Совместимость Pydantic v2/v1 для from_attributes/orm_mode ---
try:  # Pydantic v2
    from pydantic import ConfigDict

    class ORMModel(BaseModel):
        model_config = ConfigDict(from_attributes=True)

except Exception:  # Pydantic v1
    class ORMModel(BaseModel):
        class Config:
            orm_mode = True  # <-- для v1

# === Reviews ===
class ReviewCreate(BaseModel):
    product_id: int = Field(..., ge=1)
    user_id: int = Field(..., ge=1)
    text: str = Field(..., min_length=1, max_length=4000)

    # опционально (сервер может игнорировать и пересчитать)
    sentiment: Optional[str] = None
    pos_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    neg_score: Optional[float] = Field(None, ge=0.0, le=1.0)

class ReviewOut(ORMModel):
    id: int
    product_id: int
    user_id: int
    text: str
    sentiment: Optional[str] = None
    pos_score: Optional[float] = None
    neg_score: Optional[float] = None
    status: str
    created_at: datetime

# === Recommendations ===
class RecommendationCreate(BaseModel):
    user_id: int = Field(..., ge=1)
    product_id: int = Field(..., ge=1)
    score: float = Field(..., ge=0.0)

class RecommendationOut(ORMModel):
    id: int
    user_id: int
    product_id: int
    score: float
    recommended_at: Optional[datetime] = None

# === Search/Recommendation request/response ===
class QueryRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=2000)

class ProductOut(BaseModel):
    id: int
    name: str
    sentiment_score: float
    pos_percent: float
