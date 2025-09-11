# services/review_service/api/crud.py
from typing import List, Optional
import unicodedata

from fastapi import HTTPException
from sqlalchemy import func, or_
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from services.review_service.models.review import Review as ReviewModel
from services.review_service.models.recommendation import Recommendation as RecommendationModel
from services.review_service.api.schemas import ReviewCreate, RecommendationCreate
from common.models.subscriptions import Subscription, UserSubscription

# --- helpers (нормализация) ---
_SYNONYM_TO_CODE = {
    "базовий": "basic", "базовый": "basic", "basic": "basic",
    "просунутий": "advanced", "продвинутый": "advanced", "advanced": "advanced",
    "преміум": "premium", "премиум": "premium", "premium": "premium",
    "безкоштовна": "free", "бесплатная": "free", "free": "free",
}
_ALLOWED_LANGS = {"uk", "ru", "en"}

def _norm_code_or_name(value: Optional[str]) -> Optional[str]:
    if not value:
        return None
    return "-".join(unicodedata.normalize("NFKC", value).strip().lower().split())

# ---------- Reviews ----------

def get_reviews_by_product(db: Session, product_id: int) -> List[ReviewModel]:
    return db.query(ReviewModel).filter(ReviewModel.product_id == product_id).all()

def create_review(db: Session, review: ReviewCreate) -> ReviewModel:
    obj = ReviewModel(
        product_id=review.product_id,
        user_id=review.user_id,
        text=review.text,
        sentiment=review.sentiment,
        pos_score=review.pos_score,
        neg_score=review.neg_score,
        status="PENDING",
    )
    try:
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Error creating review")

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

def get_reviews_by_sentiment(db: Session, sentiment: str) -> List[ReviewModel]:
    return db.query(ReviewModel).filter(ReviewModel.sentiment == sentiment).all()

def get_reviews_by_subscription(
    db: Session,
    subscription_name: Optional[str] = None,
    subscription_id: Optional[int] = None,
    lang: Optional[str] = None,
) -> List[ReviewModel]:
    """
    Фильтр по подписке. Free=1.
    Для Free включаем отзывы пользователей с явной подпиской id=1
    И (по умолчанию) без записи в user_subscriptions (NULL).
    Уберите условие IS NULL, если нужна только явная id=1.
    """
    # Free?
    is_free = (subscription_id == 1)
    if subscription_name and not is_free:
        is_free = (_norm_code_or_name(subscription_name) == "free")

    if is_free:
        q = (
            db.query(ReviewModel)
            .outerjoin(UserSubscription, ReviewModel.user_id == UserSubscription.user_id)
            .outerjoin(Subscription, UserSubscription.subscription_id == Subscription.id)
            .filter(or_(Subscription.id == 1, UserSubscription.subscription_id.is_(None)))
        )
        if lang:
            lang_norm = lang.strip().lower()
            if lang_norm not in _ALLOWED_LANGS:
                raise HTTPException(status_code=400, detail="lang must be 'ru', 'uk' or 'en'")
            lang_col = getattr(Subscription, "language", None) or getattr(Subscription, "lang", None)
            if lang_col is not None:
                q = q.filter(
                    or_(UserSubscription.subscription_id.is_(None), func.lower(lang_col) == lang_norm)
                )
        return q.order_by(ReviewModel.created_at.desc()).all()

    # not Free: строгий INNER JOIN + точный матч
    q = (
        db.query(ReviewModel)
        .join(UserSubscription, ReviewModel.user_id == UserSubscription.user_id)
        .join(Subscription, UserSubscription.subscription_id == Subscription.id)
    )

    if subscription_id is not None:
        q = q.filter(Subscription.id == subscription_id)
    elif subscription_name:
        code = _norm_code_or_name(subscription_name)
        if not code:
            raise HTTPException(status_code=400, detail="Некорректное имя/код подписки")
        q = q.filter(func.lower(func.btrim(Subscription.code)) == code)
    else:
        raise HTTPException(status_code=400, detail="Provide subscription_id or subscription_name")

    if lang:
        lang_norm = lang.strip().lower()
        if lang_norm not in _ALLOWED_LANGS:
            raise HTTPException(status_code=400, detail="lang must be 'ru', 'uk' or 'en'")
        lang_col = getattr(Subscription, "language", None) or getattr(Subscription, "lang", None)
        if lang_col is not None:
            q = q.filter(func.lower(lang_col) == lang_norm)

    return q.order_by(ReviewModel.created_at.desc()).all()

# ---------- Recommendations ----------

def create_recommendation(db: Session, data: RecommendationCreate) -> RecommendationModel:
    obj = RecommendationModel(**data.dict())
    try:
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj
    except SQLAlchemyError:
        db.rollback()
        raise

def update_recommendation(db: Session, rec_id: int, data: RecommendationCreate) -> RecommendationModel:
    obj = db.query(RecommendationModel).filter(RecommendationModel.id == rec_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Recommendation not found")

    for k, v in data.dict().items():
        setattr(obj, k, v)

    try:
        db.commit()
        db.refresh(obj)
        return obj
    except SQLAlchemyError:
        db.rollback()
        raise

def delete_recommendation(db: Session, rec_id: int) -> None:
    obj = db.query(RecommendationModel).filter(RecommendationModel.id == rec_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    try:
        db.delete(obj)
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise

def get_recommendations_filtered(db: Session, min_score: float) -> List[RecommendationModel]:
    return (
        db.query(RecommendationModel)
        .filter(RecommendationModel.score >= min_score)
        .order_by(RecommendationModel.score.desc())
        .all()
    )
