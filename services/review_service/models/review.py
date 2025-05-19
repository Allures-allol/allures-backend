# services/review_service/models/review.py
from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime
from services.review_service.db.database import Base  # Используем общую базу

class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, index=True)
    user_id = Column(Integer, index=True)
    text = Column(String)
    sentiment = Column(String)
    pos_score = Column(Float)
    neg_score = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)

