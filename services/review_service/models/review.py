# services/review_service/models/review.py
from sqlalchemy import Column, Integer, String, Float, ForeignKey, TIMESTAMP, func
from common.db.base import Base

class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)

    # FK можно оставить — это про целостность БД, но без relationship()
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    user_id    = Column(Integer, ForeignKey("users.id"),    nullable=False)

    # данные отзыва
    text      = Column(String, nullable=False)
    sentiment = Column(String, nullable=True)
    pos_score = Column(Float,  nullable=True)
    neg_score = Column(Float,  nullable=True)
    score     = Column(Float,  nullable=True)

    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
