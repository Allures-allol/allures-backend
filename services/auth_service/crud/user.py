# 📁 services/auth_service/crud/user.py
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from common.models.user import User
from common.models.subscriptions import Subscription, UserSubscription
from common.models.payment import Payment

from services.auth_service.utils.security import hash_password, verify_password
from services.auth_service.schemas.user import UserCreate
from datetime import datetime, timedelta

# ✅ Регистрация пользователя + активация подписки "free"
def create_user(db: Session, user: UserCreate):
    db_user = User(
        login=user.login,
        password_hash=hash_password(user.password),
        full_name=user.full_name,
        email=user.email,
        phone=user.phone,
        avatar_url=user.avatar_url,
        language=user.language or "uk",
        bonus_balance=user.bonus_balance or 0,
        delivery_address=user.delivery_address,
        role=user.role or "user",
        is_blocked=user.is_blocked or False
    )
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)

        # 🔓 Автоматически активировать подписку free
        free_sub = db.query(Subscription).filter_by(name="free").first()
        if not free_sub:
            raise HTTPException(status_code=500, detail="Підписка 'free' не знайдена")

        new_subscription = UserSubscription(
            user_id=db_user.id,
            subscription_id=free_sub.id,
            start_date=datetime.utcnow(),
            end_date=datetime.utcnow() + timedelta(days=free_sub.duration_days),
            remaining_scans=free_sub.scan_limit if hasattr(free_sub, "scan_limit") else 0,
            is_active=True
        )
        db.add(new_subscription)
        db.commit()
        return db_user
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Користувач з таким логіном вже існує")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Помилка під час реєстрації: {str(e)}")

# ✅ Аутентификация пользователя (вхід)
def authenticate_user(db: Session, login: str, password: str):
    user = db.query(User).filter(User.login == login).first()

    if not user:
        raise HTTPException(status_code=404, detail="Користувача не знайдено")

    if user.is_blocked:
        raise HTTPException(status_code=403, detail="Акаунт заблоковано")

    if not verify_password(password, user.password_hash):
        raise HTTPException(status_code=401, detail="Невірний пароль")

    return user

# ✅ Отримати всіх користувачів
def get_all_users(db: Session):
    return db.query(User).all()

# ✅ Запит на скидання пароля
def forgot_password(db: Session, email: str):
    user = db.query(User).filter(User.login == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Користувача не знайдено")
    return {"message": f"Лист для скидання пароля надіслано на {email}"}

# ✅ Скидання пароля
def reset_password(db: Session, email: str, new_password: str):
    user = db.query(User).filter(User.login == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Користувача не знайдено")

    user.password_hash = hash_password(new_password)
    db.commit()
    return {"message": "Пароль успішно змінено"}

# ✅ Пошук користувача з підпискою
def get_user_by_login(db: Session, login: str):
    user = db.query(User).options(
        joinedload(User.uploads),
        joinedload(User.subscriptions).joinedload(UserSubscription.subscription)
    ).filter(User.login == login).first()

    if user:
        active_sub = next((s for s in user.subscriptions if s.is_active), None)
        user.subscription_type = active_sub.subscription.name if active_sub else "none"
    return user

# ✅ Зміна пароля
def change_password(db: Session, login: str, old_password: str, new_password: str):
    user = get_user_by_login(db, login)
    if not user or not verify_password(old_password, user.password_hash):
        return None
    user.password_hash = hash_password(new_password)
    db.commit()
    return user

# ✅ Видалення користувача
def delete_user_by_id(db: Session, user_id: int):
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        db.delete(user)
        db.commit()
        return True
    return False
