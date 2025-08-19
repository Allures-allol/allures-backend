# services/subscription_service/crud/subscription_crud.py
# services/subscription_service/crud/subscription_crud.py
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Optional, List, Tuple

from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from common.models.subscriptions import Subscription, UserSubscription
from common.models.payment import Payment

# Опциональные сущности (если они есть в проекте)
try:
    from common.models.review import Review  # noqa: F401
except Exception:  # модель может отсутствовать
    Review = None  # type: ignore

try:
    from common.models.recommendation import Recommendation  # noqa: F401
    from services.subscription_service.schemas.subscription_schemas import RecommendationCreate  # noqa: F401
except Exception:
    Recommendation = None  # type: ignore
    RecommendationCreate = None  # type: ignore


# ---------- ВСПОМОГАТЕЛЬНЫЕ ----------

_ALLOWED_LANGS = {"ru", "uk", "en"}


def _norm_code(value: Optional[str]) -> Optional[str]:
    """Нормализуем код подписки: trim + lower + замена пробелов на дефисы."""
    if not value:
        return None
    return "-".join(value.strip().lower().split())


def _get_lang_attr():
    """
    Возвращает реальный столбец языка в модели Subscription, если он есть.
    Поддерживает варианты: language, lang_code, lang.
    """
    return (
        getattr(Subscription, "language", None)
        or getattr(Subscription, "lang_code", None)
        or getattr(Subscription, "lang", None)
    )


def _apply_lang_filter(q, lang: Optional[str]):
    """Аккуратно применяем фильтр по языку, только если колонка есть и lang валиден."""
    if not lang:
        return q
    lang_norm = lang.strip().lower()
    if lang_norm not in _ALLOWED_LANGS:
        raise HTTPException(status_code=400, detail="lang must be 'ru', 'uk' or 'en'")
    lang_attr = _get_lang_attr()
    if lang_attr is not None:
        q = q.filter(func.lower(lang_attr) == lang_norm)
    return q


def _commit_or_rollback(db: Session):
    try:
        db.commit()
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"DB error: {str(e)}")


# ---------- SUBSCRIPTIONS CRUD ----------

def list_subscriptions(
    db: Session,
    lang: Optional[str] = None,
    offset: int = 0,
    limit: int = 100,
) -> List[Subscription]:
    q = db.query(Subscription)
    q = _apply_lang_filter(q, lang)
    return q.offset(max(offset, 0)).limit(min(max(limit, 1), 500)).all()


def get_subscription_by_code(
    db: Session,
    code_or_name: str,
    lang: Optional[str] = None,
) -> Optional[Subscription]:
    """
    Получить подписку по коду (приоритет) или fallback по name (нижний регистр + trim).
    """
    q = db.query(Subscription)
    q = _apply_lang_filter(q, lang)

    code = _norm_code(code_or_name)
    if code:
        q1 = q.filter(func.lower(func.btrim(Subscription.code)) == code)
        sub = q1.first()
        if sub:
            return sub

    # Fallback — точное совпадение по name (lower + trim)
    norm = code_or_name.strip().lower()
    q2 = q.filter(func.lower(func.btrim(Subscription.name)) == norm)
    return q2.first()


def get_user_active_subscription(db: Session, user_id: int) -> UserSubscription:
    us = (
        db.query(UserSubscription)
        .filter(UserSubscription.user_id == user_id, UserSubscription.is_active.is_(True))
        .first()
    )
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
    return q.offset(max(offset, 0)).limit(min(max(limit, 1), 500)).all()


def deactivate_user_subscription(db: Session, user_id: int) -> int:
    updated = (
        db.query(UserSubscription)
        .filter(UserSubscription.user_id == user_id, UserSubscription.is_active.is_(True))
        .update({"is_active": False})
    )
    _commit_or_rollback(db)
    return updated


def set_auto_renew(db: Session, user_id: int, enable: bool) -> int:
    active_sub = (
        db.query(UserSubscription)
        .filter(UserSubscription.user_id == user_id, UserSubscription.is_active.is_(True))
        .first()
    )
    if not active_sub:
        raise HTTPException(status_code=404, detail="Нет активной подписки")
    active_sub.auto_renew = bool(enable)
    _commit_or_rollback(db)
    return 1


def _deactivate_all_active(db: Session, user_id: int):
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


def activate_subscription_from_payment(db: Session, user_id: int, payment_id: int) -> UserSubscription:
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Оплата не найдена")

    sub = db.query(Subscription).filter(Subscription.id == payment.subscription_id).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Подписка не найдена")

    _deactivate_all_active(db, user_id)
    return _activate_new_subscription(db, user_id, sub, payment_id=payment.id)


def activate_subscription_by_code(
    db: Session,
    user_id: int,
    code_or_name: str,
    lang: Optional[str] = None,
) -> UserSubscription:
    sub = get_subscription_by_code(db, code_or_name, lang)
    if not sub:
        raise HTTPException(status_code=404, detail="Подписка не найдена")

    # Не даём активировать ту же активную подписку повторно
    existing = (
        db.query(UserSubscription)
        .filter(
            UserSubscription.user_id == user_id,
            UserSubscription.subscription_id == sub.id,
            UserSubscription.is_active.is_(True),
        )
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="У пользователя уже есть активная подписка с этим кодом")

    _deactivate_all_active(db, user_id)
    return _activate_new_subscription(db, user_id, sub)


# ---------- ANALYTICS / REPORTING (по аналогии со стилем reviews) ----------

def count_active_by_plan(
    db: Session,
    lang: Optional[str] = None,
) -> List[Tuple[str, int]]:
    """
    Возвращает список пар (code, count) по активным подпискам.
    Учитывает язык, если поле языка есть у модели.
    """
    q = (
        db.query(Subscription.code, func.count(UserSubscription.id))
        .join(UserSubscription, UserSubscription.subscription_id == Subscription.id)
        .filter(UserSubscription.is_active.is_(True))
        .group_by(Subscription.code)
    )
    lang_attr = _get_lang_attr()
    if lang and lang_attr is not None:
        lang_norm = lang.strip().lower()
        if lang_norm not in _ALLOWED_LANGS:
            raise HTTPException(status_code=400, detail="lang must be 'ru', 'uk' or 'en'")
        q = q.filter(func.lower(lang_attr) == lang_norm)
    return q.all()


# ---------- Связанные отзывы по подписке (если модель Review есть) ----------

def get_reviews_by_subscription(
    db: Session,
    subscription_name: Optional[str] = None,
    subscription_id: Optional[int] = None,
    lang: Optional[str] = None,
):
    """
    Возвращает отзывы пользователей, привязанные к их активной подписке.
    Требует модель Review (опционально-импортируемая).
    """
    if Review is None:
        raise HTTPException(status_code=501, detail="Review model not available")

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
            norm = subscription_name.strip().lower()
            q = q.filter(func.lower(func.btrim(Subscription.name)) == norm)
    else:
        raise HTTPException(status_code=400, detail="Provide subscription_id or subscription_name")

    q = _apply_lang_filter(q, lang)
    return q.all()


def get_reviews_by_subscription_name(
    db: Session,
    subscription_name: str,
    lang: Optional[str] = None,
):
    return get_reviews_by_subscription(db, subscription_name=subscription_name, lang=lang)


# ---------- Рекомендации (если модель Recommendation есть) ----------

def create_recommendation(db: Session, data):
    """
    Создаёт Recommendation, если модель и схема доступны.
    Ожидает pydantic-схему RecommendationCreate со стандартным .dict().
    """
    if Recommendation is None or RecommendationCreate is None:
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
