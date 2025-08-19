# services/subscription_service/routers/subscription_routers.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import List
from datetime import datetime, timedelta
from services.subscription_service.crud import subscription_crud

from common.db.session import get_db
from common.models.user import User

from services.subscription_service.schemas.subscription_schemas import (
    SubscriptionOut,
    UserSubscriptionOut
)

from services.subscription_service.crud.subscription_crud import activate_subscription_from_payment

router = APIRouter()

# Получить список подписок по языку (по умолчанию — 'uk')
@router.get("/", response_model=List[SubscriptionOut])
def get_subscriptions(language: str = "uk", db: Session = Depends(get_db)):
    return subscription_crud.get_all_subscriptions(db, language)

# POST /start-free-subscription — вручную активировать бесплатную подписку
@router.post("/start-free-subscription")
def start_free_subscription(user_id: int, language: str = "uk", db: Session = Depends(get_db)):
    new_sub = subscription_crud.activate_subscription_by_code(user_id=user_id, code="free", language=language, db=db)
    return {"message": "Бесплатная подписка успешно активирована", "subscription_id": new_sub.id}

# POST /activate — активировать платную подписку по оплате
@router.post("/activate")
def activate_subscription(user_id: int, payment_id: int, db: Session = Depends(get_db)):
    new_sub = subscription_crud.activate_subscription_from_payment(user_id=user_id, payment_id=payment_id, db=db)
    return {"message": "Подписка успешно активирована", "subscription_id": new_sub.id}

# GET /active — получить активную подписку пользователя
@router.get("/active", response_model=UserSubscriptionOut)
def get_active_subscription(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter_by(id=user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    return subscription_crud.get_user_active_subscription(db, user.id)

# PUT /auto-renew — изменить статус автопродления
@router.put("/auto-renew")
def toggle_auto_renew(user_id: int, enable: bool, db: Session = Depends(get_db)):
    updated = subscription_crud.set_auto_renew(user_id=user_id, enable=enable, db=db)
    return {"message": f"Автопродление {'включено' if enable else 'отключено'}", "updated": updated}

@router.get("/history", response_model=List[UserSubscriptionOut])
def get_subscription_history(user_id: int, db: Session = Depends(get_db)):
    return subscription_crud.get_user_subscription_history(user_id=user_id, db=db)

@router.put("/deactivate")
def deactivate_subscription(user_id: int, db: Session = Depends(get_db)):
    updated = subscription_crud.deactivate_user_subscription(user_id=user_id, db=db)
    return {"message": "Подписка деактивирована", "count": updated}
