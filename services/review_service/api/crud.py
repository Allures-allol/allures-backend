# services/review_service/api/crud.py
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError

from services.review_service.models.review import Review
from services.review_service.models.recommendation import Recommendation
from services.review_service.api.schemas import ReviewCreate, RecommendationCreate
from common.models.subscriptions import Subscription, UserSubscription

# ---- helpers ----
_SYNONYMS_TO_CODE = {
    # basic
    "базовый": "basic", "базовий": "basic", "basic": "basic",
    # advanced
    "продвинутый": "advanced", "просунутий": "advanced", "advanced": "advanced",
    # premium
    "премиум": "premium", "преміум": "premium", "premium": "premium",
}

def _norm_code(name_or_code: str) -> Optional[str]:
    if not name_or_code:
        return None
    return _SYNONYMS_TO_CODE.get(name_or_code.strip().lower())

# ---------- Reviews ----------
def create_review(db: Session, review: ReviewCreate) -> Review:
    new_review = Review(
        product_id=review.product_id,
        user_id=review.user_id,
        text=review.text,
        sentiment=getattr(review, "sentiment", None),
        pos_score=getattr(review, "pos_score", None),
        neg_score=getattr(review, "neg_score", None),
    )
    try:
        db.add(new_review)
        db.commit()
        db.refresh(new_review)
        return new_review
    except SQLAlchemyError:
        db.rollback()
        raise

def get_all_reviews(db: Session) -> List[Review]:
    return db.query(Review).order_by(Review.created_at.desc()).all()

def get_reviews_by_sentiment(db: Session, sentiment: str) -> List[Review]:
    return db.query(Review).filter(Review.sentiment == sentiment).all()

def get_reviews_by_subscription(
    db: Session,
    subscription_name: Optional[str] = None,
    subscription_id: Optional[int] = None,
    lang: Optional[str] = None,
) -> List[Review]:
    q = (
        db.query(Review)
        .join(UserSubscription, Review.user_id == UserSubscription.user_id)
        .join(Subscription, UserSubscription.subscription_id == Subscription.id)
    )

    # ID приоритетнее
    if subscription_id is not None:
        q = q.filter(Subscription.id == subscription_id)
    elif subscription_name:
        code = _norm_code(subscription_name)
        if code:
            q = q.filter(Subscription.code == code)
        else:
            # fallback: точное совпадение по name (нижний регистр+trim)
            norm = subscription_name.strip().lower()
            q = q.filter(func.lower(func.btrim(Subscription.name)) == norm)
    else:
        raise HTTPException(status_code=400, detail="Provide subscription_id or subscription_name")

    # Язык: фильтруем только если такое поле вообще существует в модели
    if lang:
        lang_norm = lang.strip().lower()
        allowed = {"ru", "uk", "en"}
        if lang_norm not in allowed:
            raise HTTPException(status_code=400, detail="lang must be 'ru', 'uk' or 'en'")

        lang_attr = getattr(Subscription, "lang_code", None) or getattr(Subscription, "lang", None)
        if lang_attr is not None:
            q = q.filter(func.lower(lang_attr) == lang_norm)

    return q.all()

# бэк-компат для старого импорта
def get_reviews_by_subscription_name(
    db: Session,
    subscription_name: str,
    lang: Optional[str] = None
) -> List[Review]:
    return get_reviews_by_subscription(db, subscription_name=subscription_name, lang=lang)

# ---------- Recommendations ----------
def create_recommendation(db: Session, data: RecommendationCreate) -> Recommendation:
    new_rec = Recommendation(**data.dict())
    try:
        db.add(new_rec)
        db.commit()
        db.refresh(new_rec)
        return new_rec
    except SQLAlchemyError:
        db.rollback()
        raise

def update_recommendation(db: Session, rec_id: int, data: RecommendationCreate) -> Recommendation:
    rec = db.query(Recommendation).filter(Recommendation.id == rec_id).first()
    if not rec:
        raise HTTPException(status_code=404, detail="Recommendation not found")

    rec.user_id = data.user_id
    rec.product_id = data.product_id
    rec.score = data.score

    try:
        db.commit()
        db.refresh(rec)
        return rec
    except SQLAlchemyError:
        db.rollback()
        raise

def delete_recommendation(db: Session, rec_id: int) -> None:
    rec = db.query(Recommendation).filter(Recommendation.id == rec_id).first()
    if not rec:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    try:
        db.delete(rec)
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise

def get_recommendations_filtered(db: Session, min_score: float) -> List[Recommendation]:
    return (
        db.query(Recommendation)
        .filter(Recommendation.score >= min_score)
        .order_by(Recommendation.score.desc())
        .all()
    )