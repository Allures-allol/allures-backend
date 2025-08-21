# services/subscription_service/crud/subscription_crud.py
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Optional, List, Tuple

from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from common.models.subscriptions import Subscription, UserSubscription

# --------- constants / helpers ---------
_ALLOWED_LANGS = {"uk", "ru", "en"}

def _norm(value: str) -> str:
    """Нормализация: lower + trim + пробелы -> дефисы (как в отзывах)."""
    return "-".join(value.strip().lower().split())

def _commit_or_rollback(db: Session) -> None:
    try:
        db.commit()
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"DB error: {str(e)}")

# --------- subscriptions: list / lookup ---------

def list_subscriptions(
    db: Session,
    lang: Optional[str] = None,
    offset: int = 0,
    limit: int = 100,
) -> List[Subscription]:
    q = db.query(Subscription)
    if lang:
        lang_norm = lang.strip().lower()
        if lang_norm not in _ALLOWED_LANGS:
            raise HTTPException(status_code=400, detail="lang must be 'uk', 'ru' or 'en'")
        q = q.filter(func.lower(Subscription.language) == lang_norm)
    return q.order_by(Subscription.id.asc()).offset(offset).limit(limit).all()

def get_subscription_by_code(
    db: Session,
    code_or_name: str,
    lang: Optional[str] = None,
) -> Optional[Subscription]:
    if not code_or_name:
        return None
    code_or_name = _norm(code_or_name)

    q = db.query(Subscription)
    if lang:
        lang_norm = lang.strip().lower()
        if lang_norm not in _ALLOWED_LANGS:
            raise HTTPException(status_code=400, detail="lang must be 'uk', 'ru' or 'en'")
        q = q.filter(func.lower(Subscription.language) == lang_norm)

    # name_norm: lower(trim(name)) с пробелами -> '-'
    name_norm = func.replace(func.lower(func.btrim(Subscription.name)), " ", "-")
    q = q.filter(
        (func.lower(Subscription.code) == code_or_name) |
        (name_norm == code_or_name)
    )
    return q.first()

# --------- user subscriptions ---------

def get_user_active_subscription(db: Session, user_id: int) -> UserSubscription:
    us = db.query(UserSubscription).filter(
        UserSubscription.user_id == user_id,
        UserSubscription.is_active.is_(True),
    ).first()
    if not us:
        raise HTTPException(status_code=404, detail="Нет активной подписки")
    return us

def get_user_subscription_history(
    db: Session,
    user_id: int,
    offset: int = 0,
    limit: int = 100,
) -> List[UserSubscription]:
    q = (
        db.query(UserSubscription)
        .filter(UserSubscription.user_id == user_id)
        .order_by(UserSubscription.start_date.desc())
    )
    offset = max(0, offset)
    limit = min(max(1, limit), 500)
    return q.offset(offset).limit(limit).all()

def deactivate_user_subscription(db: Session, user_id: int) -> int:
    updated = db.query(UserSubscription).filter(
        UserSubscription.user_id == user_id,
        UserSubscription.is_active.is_(True),
    ).update({"is_active": False})
    _commit_or_rollback(db)
    return updated

def set_auto_renew(db: Session, user_id: int, enable: bool) -> int:
    active_sub = db.query(UserSubscription).filter(
        UserSubscription.user_id == user_id,
        UserSubscription.is_active.is_(True),
    ).first()
    if not active_sub:
        raise HTTPException(status_code=404, detail="Нет активной подписки")
    active_sub.auto_renew = bool(enable)
    _commit_or_rollback(db)
    return 1

def _deactivate_all_active(db: Session, user_id: int) -> None:
    db.query(UserSubscription).filter(
        UserSubscription.user_id == user_id,
        UserSubscription.is_active.is_(True),
    ).update({"is_active": False})

def _activate_new_subscription(
    db: Session,
    user_id: int,
    sub: Subscription,
    payment_id: Optional[int] = None,
) -> UserSubscription:
    now = datetime.utcnow()
    new_sub = UserSubscription(
        user_id=user_id,
        subscription_id=sub.id,
        start_date=now,
        end_date=now + timedelta(days=sub.duration_days),
        is_active=True,
        auto_renew=True,
        payment_id=payment_id,
    )
    db.add(new_sub)
    _commit_or_rollback(db)
    db.refresh(new_sub)
    return new_sub

def activate_subscription_by_code(
    db: Session,
    user_id: int,
    code_or_name: str,
    lang: Optional[str] = None,
) -> UserSubscription:
    sub = get_subscription_by_code(db, code_or_name, lang)
    if not sub:
        raise HTTPException(status_code=404, detail="Подписка не найдена")

    existing = db.query(UserSubscription).filter(
        UserSubscription.user_id == user_id,
        UserSubscription.subscription_id == sub.id,
        UserSubscription.is_active.is_(True),
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="У пользователя уже есть активная подписка с этим кодом")

    _deactivate_all_active(db, user_id)
    return _activate_new_subscription(db, user_id, sub)

# --------- payments (ленивый импорт) ---------

def activate_subscription_from_payment(db: Session, user_id: int, payment_id: int) -> UserSubscription:
    try:
        from common.models.payment import Payment  # импорт только здесь
    except Exception:
        raise HTTPException(status_code=501, detail="Payment model not available")

    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Оплата не найдена")

    sub = db.query(Subscription).filter(Subscription.id == payment.subscription_id).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Подписка не найдена")

    _deactivate_all_active(db, user_id)
    return _activate_new_subscription(db, user_id, sub, payment_id=payment.id)

# --------- analytics ---------

def count_active_by_plan(db: Session, lang: Optional[str] = None) -> List[Tuple[str, int]]:
    q = (
        db.query(Subscription.code, func.count(UserSubscription.id))
        .join(UserSubscription, UserSubscription.subscription_id == Subscription.id)
        .filter(UserSubscription.is_active.is_(True))
        .group_by(Subscription.code)
    )
    if lang:
        lang_norm = lang.strip().lower()
        if lang_norm not in _ALLOWED_LANGS:
            raise HTTPException(status_code=400, detail="lang must be 'uk', 'ru' or 'en'")
        q = q.filter(func.lower(Subscription.language) == lang_norm)
    return q.all()

# --------- reviews (полностью опционально и лениво) ---------

def get_reviews_by_subscription(
    db: Session,
    subscription_name: Optional[str] = None,
    subscription_id: Optional[int] = None,
    lang: Optional[str] = None,
):
    try:
        from common.models.review import Review  # импорт только при вызове
    except Exception:
        raise HTTPException(status_code=501, detail="Review model not available")

    q = (
        db.query(Review)
        .join(UserSubscription, Review.user_id == UserSubscription.user_id)
        .join(Subscription, UserSubscription.subscription_id == Subscription.id)
    )

    if subscription_id is not None:
        q = q.filter(Subscription.id == subscription_id)
    elif subscription_name:
        code_or_name = _norm(subscription_name)
        name_norm = func.replace(func.lower(func.btrim(Subscription.name)), " ", "-")
        q = q.filter(
            (func.lower(Subscription.code) == code_or_name) |
            (name_norm == code_or_name)
        )
    else:
        raise HTTPException(status_code=400, detail="Provide subscription_id or subscription_name")

    if lang:
        lang_norm = lang.strip().lower()
        if lang_norm not in _ALLOWED_LANGS:
            raise HTTPException(status_code=400, detail="lang must be 'uk', 'ru' or 'en'")
        q = q.filter(func.lower(Subscription.language) == lang_norm)

    return q.all()

def get_reviews_by_subscription_name(db: Session, subscription_name: str, lang: Optional[str] = None):
    return get_reviews_by_subscription(db, subscription_name=subscription_name, lang=lang)

# --------- recommendations (тоже лениво и опционально) ---------

def create_recommendation(db: Session, data):
    try:
        from services.review_service.api.schemas import RecommendationCreate
        from services.review_service.models.recommendation import Recommendation
    except Exception:
        raise HTTPException(status_code=501, detail="Recommendation model/schema not available")

    if not isinstance(data, RecommendationCreate):
        raise HTTPException(status_code=400, detail="Invalid payload type for RecommendationCreate")

    new_rec = Recommendation(**data.dict())
    try:
        db.add(new_rec)
        db.commit()
        db.refresh(new_rec)
        return new_rec
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"DB error: {str(e)}")
