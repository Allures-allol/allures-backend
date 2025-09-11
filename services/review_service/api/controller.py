# services/review_service/api/controller.py
from typing import List
from fastapi import HTTPException
from sqlalchemy.orm import Session

from services.review_service.models.review import Review as ReviewModel
from services.review_service.models.recommendation import Recommendation as RecommendationModel
from services.review_service.api.schemas import ReviewCreate

# анализатор может отсутствовать в dev — сделаем graceful fallback
try:
    from services.review_service.sentiment.analyzer import analyze_sentiment  # noqa
except Exception:
    def analyze_sentiment(text: str):
        # очень грубая заглушка
        txt = (text or "").lower()
        pos = 0.7 if "good" in txt or "клас" in txt or "супер" in txt else 0.3
        return {"sentiment": "positive" if pos >= 0.5 else "negative",
                "pos_score": pos,
                "neg_score": 1 - pos}

# --------- Reviews ----------
def create_review(db: Session, review_data: ReviewCreate) -> ReviewModel:
    res = analyze_sentiment(review_data.text)

    new_review = ReviewModel(
        product_id=review_data.product_id,
        user_id=review_data.user_id,
        text=review_data.text,
        sentiment=res.get("sentiment"),
        pos_score=res.get("pos_score"),
        neg_score=res.get("neg_score"),
        status="PENDING",
    )
    try:
        db.add(new_review)
        db.commit()
        db.refresh(new_review)
        return new_review
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error saving review: {e}")

def get_reviews_by_product(db: Session, product_id: int) -> List[ReviewModel]:
    return db.query(ReviewModel).filter(ReviewModel.product_id == product_id).all()

def get_all_reviews(db: Session) -> List[ReviewModel]:
    return db.query(ReviewModel).all()

def get_reviews_by_status(db: Session, status: str) -> List[ReviewModel]:
    return db.query(ReviewModel).filter(ReviewModel.status == status).all()

def update_review_status(db: Session, review_id: int, status: str) -> ReviewModel:
    allowed = {"PENDING", "APPROVED", "REJECTED"}
    if status not in allowed:
        raise HTTPException(status_code=400, detail=f"Invalid status. Choose {', '.join(allowed)}.")

    obj = db.query(ReviewModel).filter(ReviewModel.id == review_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Review not found")

    obj.status = status
    db.commit()
    db.refresh(obj)
    return obj

# --------- Recommendations ----------
def save_recommendation(db: Session, user_id: int, product_id: int, score: float) -> RecommendationModel:
    rec = RecommendationModel(user_id=user_id, product_id=product_id, score=score)
    try:
        db.add(rec)
        db.commit()
        db.refresh(rec)
        return rec
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error saving recommendation: {e}")

def get_all_recommendations(db: Session):
    return db.query(RecommendationModel).all()
