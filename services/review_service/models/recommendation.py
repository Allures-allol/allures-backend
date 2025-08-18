# services/review_service/models/recommendation.py
from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, func, Index
from common.db.base import Base

class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    score = Column(Float, nullable=False)
    recommended_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # опционально — читаемее в логах
    def __repr__(self) -> str:
        return f"<Recommendation id={self.id} user_id={self.user_id} product_id={self.product_id} score={self.score}>"

# Доп. индексы (если хочешь явно, но выше уже index=True на колонках)
Index("ix_recommendations_user", Recommendation.user_id)
Index("ix_recommendations_product", Recommendation.product_id)

