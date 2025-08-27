from sqlalchemy import Column, Integer, String, Float, ForeignKey, TIMESTAMP, func
from sqlalchemy.orm import relationship
from common.db.base import Base

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
    lang = Column(String(2), nullable=False, server_default="uk")  # 👈 добавлено
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    # без back_populates
    user = relationship("User", lazy="joined")
    product = relationship("Product", lazy="joined")
