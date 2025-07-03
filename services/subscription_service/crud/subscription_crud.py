# services/subscription_service/crud/subscription_crud.py
from sqlalchemy.orm import Session
from fastapi import HTTPException
from datetime import datetime, timedelta

from common.models.subscriptions import Subscription, UserSubscription
from common.models.payment import Payment


def get_all_subscriptions(db: Session):
    return db.query(Subscription).all()


def get_subscription_by_name(db: Session, name: str):
    return db.query(Subscription).filter(Subscription.name == name).first()


def get_user_active_subscription(db: Session, user_id: int):
    user_sub = (
        db.query(UserSubscription)
        .filter(UserSubscription.user_id == user_id, UserSubscription.is_active == True)
        .first()
    )
    if not user_sub:
        raise HTTPException(status_code=404, detail="Нет активной подписки")
    return user_sub


def activate_subscription_from_payment(user_id: int, payment_id: int, db: Session):
    payment = db.query(Payment).filter_by(id=payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Оплата не найдена")

    sub = db.query(Subscription).filter_by(id=payment.subscription_id).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Подписка не найдена")

    # Деактивировать текущую
    db.query(UserSubscription).filter_by(user_id=user_id, is_active=True).update({"is_active": False})

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
    db.refresh(new_sub)
    return new_sub


def create_default_subscription_for_user(user_id: int, db: Session):
    base_sub = db.query(Subscription).filter_by(name="Базовый").first()
    if not base_sub:
        raise HTTPException(status_code=404, detail="Базовая подписка не найдена")

    user_sub = UserSubscription(
        user_id=user_id,
        subscription_id=base_sub.id,
        start_date=datetime.utcnow(),
        end_date=datetime.utcnow() + timedelta(days=base_sub.duration_days),
        is_active=True
    )
    db.add(user_sub)
    db.commit()
    db.refresh(user_sub)
    return user_sub
