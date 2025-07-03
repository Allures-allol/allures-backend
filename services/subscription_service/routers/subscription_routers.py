# services/subscription_service/routers/subscription_routers.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import List
from datetime import datetime, timedelta

from common.db.session import get_db
from common.models.user import User
from common.models.subscriptions import Subscription, UserSubscription
from common.models.payment import Payment

from services.subscription_service.schemas.subscription_schemas import (
    SubscriptionOut,
    UserSubscriptionOut
)

router = APIRouter()

# Получить список подписок
@router.get("/", response_model=List[SubscriptionOut])
def get_subscriptions(db: Session = Depends(get_db)):
    return db.query(Subscription).all()

# Вспомогательная функция
def activate_subscription_from_payment(user_id: int, payment_id: int, db: Session):
    payment = db.query(Payment).filter_by(id=payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Оплата не найдена")

    sub = db.query(Subscription).filter_by(id=payment.subscription_id).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Подписка не найдена")

    # Деактивация старых подписок
    db.query(UserSubscription).filter_by(user_id=user_id, is_active=True).update({"is_active": False})

    # Новая подписка
    new_sub = UserSubscription(
        user_id=user_id,
        subscription_id=sub.id,
        start_date=datetime.utcnow(),
        end_date=datetime.utcnow() + timedelta(days=sub.duration_days),
        is_active=True,
        payment_id=payment.id
    )
    db.add(new_sub)
    db.commit()

# POST /activate — активация после оплаты
@router.post("/activate")
def activate_subscription(user_id: int, payment_id: int, db: Session = Depends(get_db)):
    activate_subscription_from_payment(user_id=user_id, payment_id=payment_id, db=db)
    return {"message": "Subscription activated"}

# GET /active — получить активную подписку пользователя
@router.get("/active", response_model=UserSubscriptionOut)
def get_active_subscription(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter_by(id=user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    user_sub = (
        db.query(UserSubscription)
        .options(joinedload(UserSubscription.subscription))
        .filter_by(user_id=user.id, is_active=True)
        .first()
    )
    if not user_sub:
        raise HTTPException(status_code=404, detail="Нет активной подписки")

    return user_sub


