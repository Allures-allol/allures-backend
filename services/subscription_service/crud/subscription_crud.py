# services/subscription_service/crud/subscription_crud.py
from sqlalchemy.orm import Session
from fastapi import HTTPException
from datetime import datetime, timedelta

from common.models.subscriptions import Subscription, UserSubscription
from common.models.payment import Payment

# Получить все подписки (можно использовать с фильтром по языку)
def get_all_subscriptions(db: Session, language: str = "uk"):
    return db.query(Subscription).filter_by(language=language).all()

# Получить подписку по коду и языку
def get_subscription_by_code(db: Session, code: str, language: str = "uk"):
    return db.query(Subscription).filter_by(code=code, language=language).first()

# Получить активную подписку пользователя
def get_user_active_subscription(db: Session, user_id: int):
    user_sub = db.query(UserSubscription).filter_by(user_id=user_id, is_active=True).first()
    if not user_sub:
        raise HTTPException(status_code=404, detail="Нет активной подписки")
    return user_sub

# Получить всю историю подписок пользователя
def get_user_subscription_history(user_id: int, db: Session):
    return db.query(UserSubscription).filter_by(user_id=user_id).order_by(UserSubscription.start_date.desc()).all()

# Деактивировать текущую подписку
def deactivate_user_subscription(user_id: int, db: Session):
    updated = db.query(UserSubscription).filter_by(user_id=user_id, is_active=True).update({"is_active": False})
    db.commit()
    return updated

# Изменить статус автопродления
def set_auto_renew(user_id: int, enable: bool, db: Session):
    active_sub = db.query(UserSubscription).filter_by(user_id=user_id, is_active=True).first()
    if not active_sub:
        raise HTTPException(status_code=404, detail="Нет активной подписки")

    active_sub.auto_renew = enable
    db.commit()
    return 1

# Активировать подписку по платежу
def activate_subscription_from_payment(user_id: int, payment_id: int, db: Session):
    payment = db.query(Payment).filter_by(id=payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Оплата не найдена")

    sub = db.query(Subscription).filter_by(id=payment.subscription_id).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Подписка не найдена")

    db.query(UserSubscription).filter_by(user_id=user_id, is_active=True).update({"is_active": False})

    new_sub = UserSubscription(
        user_id=user_id,
        subscription_id=sub.id,
        start_date=datetime.utcnow(),
        end_date=datetime.utcnow() + timedelta(days=sub.duration_days),
        is_active=True,
        auto_renew=True,
        payment_id=payment.id
    )
    db.add(new_sub)
    db.commit()
    db.refresh(new_sub)
    return new_sub

# Активировать подписку по коду (например, free)
def activate_subscription_by_code(user_id: int, code: str, language: str, db: Session):
    sub = get_subscription_by_code(db, code, language)
    if not sub:
        raise HTTPException(status_code=404, detail="Подписка не найдена")

    existing = db.query(UserSubscription).filter_by(user_id=user_id, subscription_id=sub.id, is_active=True).first()
    if existing:
        raise HTTPException(status_code=400, detail="У пользователя уже есть активная подписка с этим кодом")

    db.query(UserSubscription).filter_by(user_id=user_id, is_active=True).update({"is_active": False})

    new_sub = UserSubscription(
        user_id=user_id,
        subscription_id=sub.id,
        start_date=datetime.utcnow(),
        end_date=datetime.utcnow() + timedelta(days=sub.duration_days),
        is_active=True,
        auto_renew=True
    )
    db.add(new_sub)
    db.commit()
    db.refresh(new_sub)
    return new_sub