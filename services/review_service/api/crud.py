# services/review_service/api/crud.py
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
import unicodedata
from services.review_service.models.review import Review
from services.review_service.models.recommendation import Recommendation
from services.review_service.api.schemas import ReviewCreate, RecommendationCreate
from common.models.subscriptions import Subscription, UserSubscription

_SYNONYM_TO_CODE = {
    "базовий": "basic", "базовый": "basic", "basic": "basic",
    "просунутий": "advanced", "продвинутый": "advanced", "advanced": "advanced",
    "преміум": "premium", "премиум": "premium", "premium": "premium",
    "безкоштовна": "free", "бесплатная": "free", "free": "free",
}

_ALLOWED_LANGS = {"uk", "ru", "en"}


def _norm(s: Optional[str]) -> Optional[str]:
    if s is None:
        return None
    return unicodedata.normalize("NFKC", s).strip().lower()


def _norm_code_or_name(value: Optional[str]) -> Optional[str]:
    if not value:
        return None
    return "-".join(value.strip().lower().split())


def _normalize_code_from_name(subscription_name: Optional[str]) -> Optional[str]:
    if not subscription_name:
        return None
    norm = subscription_name.strip().lower()
    return _SYNONYM_TO_CODE.get(norm) or _norm_code_or_name(subscription_name)

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
    """
    Строгий фильтр по конкретной подписке.
    Free = id 1. Для Free берём:
      - записи, где subscription_id == 1
      - ИЛИ у пользователя нет записи в user_subscriptions (NULL)
        (если НЕ нужно включать пользователей без подписки — см. комментарий ниже)
    Остальные планы — точный матч по id или code.
    """

    # Определяем, запрошена ли Free
    is_free = False
    if subscription_id == 1:
        is_free = True
    elif subscription_name:
        code = _normalize_code_from_name(subscription_name)
        if code == "free":
            is_free = True

    if is_free:
        # LEFT OUTER JOIN, чтобы захватить пользователей без записи о подписке
        q = (
            db.query(Review)
            .outerjoin(UserSubscription, Review.user_id == UserSubscription.user_id)
            .outerjoin(Subscription, UserSubscription.subscription_id == Subscription.id)
            .filter(
                or_(
                    Subscription.id == 1,
                    UserSubscription.subscription_id.is_(None)  # <-- УБЕРИ эту строку, если нужно только id=1
                )
            )
        )

        # Язык: применяем только к строкам, где подписка реально есть (id=1); для NULL — не ограничиваем
        if lang:
            lang_norm = lang.strip().lower()
            if lang_norm not in _ALLOWED_LANGS:
                raise HTTPException(status_code=400, detail="lang must be 'ru', 'uk' or 'en'")

            lang_col = getattr(Subscription, "language", None) or getattr(Subscription, "lang", None)
            if lang_col is not None:
                q = q.filter(
                    or_(
                        UserSubscription.subscription_id.is_(None),
                        func.lower(lang_col) == lang_norm
                    )
                )

        return q.order_by(Review.created_at.desc()).all()

    # НЕ Free: строгий INNER JOIN + точный матч
    q = (
        db.query(Review)
        .join(UserSubscription, Review.user_id == UserSubscription.user_id)
        .join(Subscription, UserSubscription.subscription_id == Subscription.id)
    )

    if subscription_id is not None:
        q = q.filter(Subscription.id == subscription_id)
    elif subscription_name:
        code = _normalize_code_from_name(subscription_name)
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

    return q.order_by(Review.created_at.desc()).all()


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