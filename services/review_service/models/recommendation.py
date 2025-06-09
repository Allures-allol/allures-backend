# ✅ services/review_service/models/recommendation.py

from sqlalchemy import Column, Integer, Float, DateTime
from sqlalchemy.sql import func
from common.db.base import Base

class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    product_id = Column(Integer, nullable=False)
    score = Column(Float, nullable=False)
    recommended_at = Column(DateTime, default=func.now())

