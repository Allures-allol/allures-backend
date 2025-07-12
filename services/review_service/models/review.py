# services/review_service/models/review.py
from sqlalchemy import Column, Integer, String, Float, ForeignKey, TIMESTAMP, func
from sqlalchemy.orm import relationship
from common.db.base import Base
from common.models.products import Product
from common.models.user import User

class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    text = Column(String, nullable=False)
    sentiment = Column(String)
    pos_score = Column(Float)
    neg_score = Column(Float)
    score = Column(Float)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="reviews", lazy="joined")
    product = relationship("Product", back_populates="reviews", lazy="joined")
