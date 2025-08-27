# services/subscription_service/routers/subscription_routers.py
from __future__ import annotations

from typing import List, Optional, Tuple

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from common.db.session import get_db
from common.models.subscriptions import Subscription
from services.subscription_service.utils.security import get_user_id_optional
from services.subscription_service.crud import subscription_crud
from services.subscription_service.schemas.subscription_schemas import (
    SubscriptionOut,
    UserSubscriptionOut,
)

# ВАЖНО: теги — так Swagger будет честно показывать /subscription/...
router = APIRouter()

# ---- helpers ----

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
    return "-".join(value.strip().lower().split())

def _normalize_code_from_name(subscription_name: Optional[str]) -> Optional[str]:
    if not subscription_name:
        return None
    norm = subscription_name.strip().lower()
    return _SYNONYM_TO_CODE.get(norm) or _norm_code_or_name(subscription_name)

# ---- routes ----

@router.get("/", response_model=List[SubscriptionOut])
def list_subscriptions(
    lang: Optional[str] = Query(None, description="uk|ru|en (опционально)"),
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    if lang and lang.strip().lower() not in _ALLOWED_LANGS:
        raise HTTPException(status_code=400, detail="lang must be 'uk', 'ru' or 'en'")
    return subscription_crud.list_subscriptions(db, lang=lang, offset=offset, limit=limit)

@router.get("/lookup", response_model=SubscriptionOut)
def lookup_subscription(
    subscription_id: Optional[int] = Query(None, description="ID подписки"),
    subscription_name: Optional[str] = Query(
        None,
        description="Безкоштовна/Бесплатная/Free, Базовий/Базовый/Basic, Просунутий/Продвинутый/Advanced, Преміум/Премиум/Premium",
    ),
    lang: Optional[str] = Query(None, description="uk|ru|en (опционально)"),
    db: Session = Depends(get_db),
):
    if lang and lang.strip().lower() not in _ALLOWED_LANGS:
        raise HTTPException(status_code=400, detail="lang must be 'uk', 'ru' or 'en'")

    if subscription_id is not None:
        sub = db.query(Subscription).filter(Subscription.id == subscription_id).first()
        if not sub:
            raise HTTPException(status_code=404, detail="Подписка не найдена")
        if lang and (sub.language or "").lower() != lang.lower():
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
        raise HTTPException(status_code=400, detail="lang must be 'uk', 'ru' or 'en'")
    new_sub = subscription_crud.activate_subscription_by_code(
        db, user_id=user_id, code_or_name="free", lang=lang
    )
    return {"message": "Бесплатная подписка успешно активирована", "subscription_id": new_sub.id}

@router.post("/activate-by-code")
def activate_by_code(
    user_id: int,
    subscription_name: str = Query(..., description="basic/advanced/premium/free или аналоги (UK/RU/EN)"),
    lang: Optional[str] = Query(None, description="uk|ru|en (опционально)"),
    db: Session = Depends(get_db),
):
    if lang and lang.strip().lower() not in _ALLOWED_LANGS:
        raise HTTPException(status_code=400, detail="lang must be 'uk', 'ru' or 'en'")

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
    user_id_q: Optional[int] = Query(None, description="временный фоллбек"),
    user_id_tok: Optional[int] = Depends(get_user_id_optional),
    db: Session = Depends(get_db),
):
    user_id = user_id_tok or user_id_q
    if not user_id:
        raise HTTPException(status_code=401, detail="Auth required")
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
    lang: Optional[str] = Query(None, description="ru|uk|en (опционально)"),
    db: Session = Depends(get_db),
) -> List[Tuple[str, int]]:
    if lang and lang.strip().lower() not in _ALLOWED_LANGS:
        raise HTTPException(status_code=400, detail="lang must be 'uk', 'ru' or 'en'")
    return subscription_crud.count_active_by_plan(db, lang=lang)

# 🔹 НОВОЕ! Активировать подписку по платежу (user_id, payment_id)
@router.post("/activate-subscription")
def activate_subscription_from_payment(
    user_id: int = Query(..., description="ID пользователя"),
    payment_id: int = Query(..., description="ID платежа"),
    db: Session = Depends(get_db),
):
    """
    Активирует подписку на основании записи в payments.
    Ожидает, что у платежа заполнен subscription_id (или ваша логика это определяет).
    """
    new_sub = subscription_crud.activate_subscription_from_payment(db, user_id=user_id, payment_id=payment_id)
    return {"message": "Подписка активирована по платежу", "user_subscription_id": new_sub.id}
