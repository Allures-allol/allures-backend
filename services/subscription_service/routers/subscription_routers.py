# services/subscription_service/routers/subscription_routers.py
# services/subscription_service/routers/subscription_routers.py

from __future__ import annotations
from typing import List, Optional, Tuple

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from common.db.session import get_db
from common.models.subscriptions import Subscription, UserSubscription  # <-- singular module

from services.subscription_service.crud import subscription_crud
from services.subscription_service.schemas.subscription_schemas import (
    SubscriptionOut,
    UserSubscriptionOut,
)

router = APIRouter()

# ---- helpers ----

_SYNONYM_TO_CODE = {
    # basic
    "базовий": "basic", "базовый": "basic", "basic": "basic",
    # advanced
    "просунутий": "advanced", "продвинутый": "advanced", "advanced": "advanced",
    # premium
    "преміум": "premium", "премиум": "premium", "premium": "premium",
    # free
    "безкоштовна": "free", "бесплатная": "free", "free": "free",
}

_ALLOWED_LANGS = {"ru", "uk", "en"}


def _norm_code_or_name(value: Optional[str]) -> Optional[str]:
    if not value:
        return None
    return "-".join(value.strip().lower().split())


def _normalize_code_from_name(subscription_name: Optional[str]) -> Optional[str]:
    if not subscription_name:
        return None
    norm = subscription_name.strip().lower()
    return _SYNONYM_TO_CODE.get(norm) or _norm_code_or_name(subscription_name)


# ---- routes ----

@router.get("/", response_model=List[SubscriptionOut])
def list_subscriptions(
    lang: Optional[str] = Query(None, description="Фильтр по языку ('ru'|'uk'|'en')"),
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    if lang and lang.strip().lower() not in _ALLOWED_LANGS:
        raise HTTPException(status_code=400, detail="lang must be 'ru', 'uk' or 'en'")
    return subscription_crud.list_subscriptions(db, lang=lang, offset=offset, limit=limit)


@router.get("/lookup", response_model=SubscriptionOut)
def lookup_subscription(
    subscription_id: Optional[int] = Query(None, description="ID подписки"),
    subscription_name: Optional[str] = Query(
        None,
        description="Имя/код/синоним: Базовий|Базовый|basic / Просунутий|Продвинутый|advanced / Преміум|Премиум|premium / free",
    ),
    lang: Optional[str] = Query(None, description="Фильтр по языку ('ru'|'uk'|'en')"),
    db: Session = Depends(get_db),
):
    if lang and lang.strip().lower() not in _ALLOWED_LANGS:
        raise HTTPException(status_code=400, detail="lang must be 'ru', 'uk' or 'en'")

    if subscription_id is not None:
        sub = db.query(Subscription).filter(Subscription.id == subscription_id).first()
        if not sub:
            raise HTTPException(status_code=404, detail="Подписка не найдена")
        # если указан lang — проверим соответствие (если в модели есть колонка языка)
        if lang:
            lang_attr = (
                getattr(Subscription, "language", None)
                or getattr(Subscription, "lang_code", None)
                or getattr(Subscription, "lang", None)
            )
            if lang_attr is not None:
                # InstrumentedAttribute имеет .key; достаём значение у объекта
                attr_name = getattr(lang_attr, "key", "language")
                sub_lang = getattr(sub, attr_name, None)
                if sub_lang and sub_lang.lower() != lang.lower():
                    raise HTTPException(status_code=404, detail="Подписка с таким языком не найдена")
        return sub

    if subscription_name:
        code_or_name = _normalize_code_from_name(subscription_name)
        sub = subscription_crud.get_subscription_by_code(db, code_or_name, lang=lang)
        if not sub:
            raise HTTPException(status_code=404, detail="Подписка не найдена")
        return sub

    raise HTTPException(status_code=400, detail="Provide subscription_id or subscription_name")


@router.post("/start-free-subscription")
def start_free_subscription(
    user_id: int,
    lang: Optional[str] = Query("uk"),
    db: Session = Depends(get_db),
):
    if lang and lang.strip().lower() not in _ALLOWED_LANGS:
        raise HTTPException(status_code=400, detail="lang must be 'ru', 'uk' or 'en'")
    new_sub = subscription_crud.activate_subscription_by_code(
        db, user_id=user_id, code_or_name="free", lang=lang
    )
    return {"message": "Бесплатная подписка успешно активирована", "subscription_id": new_sub.id}


@router.post("/activate")
def activate_subscription(
    user_id: int,
    payment_id: int,
    db: Session = Depends(get_db),
):
    new_sub = subscription_crud.activate_subscription_from_payment(
        db, user_id=user_id, payment_id=payment_id
    )
    return {"message": "Подписка успешно активирована", "subscription_id": new_sub.id}


@router.post("/activate-by-code")
def activate_by_code(
    user_id: int,
    subscription_name: str = Query(
        ..., description="Имя/код/синоним: basic/advanced/premium/free или их аналоги на RU/UK"
    ),
    lang: Optional[str] = Query(None, description="Фильтр по языку ('ru'|'uk'|'en')"),
    db: Session = Depends(get_db),
):
    if lang and lang.strip().lower() not in _ALLOWED_LANGS:
        raise HTTPException(status_code=400, detail="lang must be 'ru', 'uk' or 'en'")

    code_or_name = _normalize_code_from_name(subscription_name)
    if not code_or_name:
        raise HTTPException(status_code=400, detail="Некорректное имя/код подписки")

    code_or_name = _SYNONYM_TO_CODE.get(code_or_name, code_or_name)

    new_sub = subscription_crud.activate_subscription_by_code(
        db, user_id=user_id, code_or_name=code_or_name, lang=lang
    )
    return {"message": "Подписка активирована", "subscription_id": new_sub.id}


@router.get("/active", response_model=UserSubscriptionOut)
def get_active_subscription(
    user_id: int,
    db: Session = Depends(get_db),
):
    # сервис независимый: не проверяем наличие пользователя в чужой БД
    return subscription_crud.get_user_active_subscription(db, user_id)


@router.put("/auto-renew")
def toggle_auto_renew(
    user_id: int,
    enable: bool,
    db: Session = Depends(get_db),
):
    updated = subscription_crud.set_auto_renew(db, user_id=user_id, enable=enable)
    return {"message": f"Автопродление {'включено' if enable else 'отключено'}", "updated": updated}


@router.get("/history", response_model=List[UserSubscriptionOut])
def get_subscription_history(
    user_id: int,
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    return subscription_crud.get_user_subscription_history(db, user_id=user_id, offset=offset, limit=limit)


@router.put("/deactivate")
def deactivate_subscription(
    user_id: int,
    db: Session = Depends(get_db),
):
    updated = subscription_crud.deactivate_user_subscription(db, user_id=user_id)
    return {"message": "Подписка деактивирована", "count": updated}


@router.get("/stats/active-by-plan")
def stats_active_by_plan(
    lang: Optional[str] = Query(None, description="Фильтр по языку ('ru'|'uk'|'en')"),
    db: Session = Depends(get_db),
) -> List[Tuple[str, int]]:
    if lang and lang.strip().lower() not in _ALLOWED_LANGS:
        raise HTTPException(status_code=400, detail="lang must be 'ru', 'uk' or 'en'")
    return subscription_crud.count_active_by_plan(db, lang=lang)
