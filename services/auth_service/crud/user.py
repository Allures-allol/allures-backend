# services/auth_service/crud/user.py
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from common.models.user import User
from services.auth_service.utils.security import hash_password, verify_password
from services.auth_service.schemas.user import UserCreate

# ✅ Регистрация пользователя
def create_user(db: Session, user: UserCreate):
    db_user = User(
        login=user.login,
        password=hash_password(user.password),
        full_name=user.full_name,
        email=user.email,
        phone=user.phone,
        avatar_url=user.avatar_url,
        language=user.language or "uk",
        bonus_balance=user.bonus_balance or 0,
        delivery_address=user.delivery_address,
        role="user",            # можно заменить на user.role если нужно
        is_blocked=False        # можно заменить на user.is_blocked если нужно
    )
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
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

    if not verify_password(password, user.password):
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

    # Тут може бути логіка відправки листа
    return {"message": f"Лист для скидання пароля надіслано на {email}"}

# ✅ Скидання пароля
def reset_password(db: Session, email: str, new_password: str):
    user = db.query(User).filter(User.login == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Користувача не знайдено")

    user.password = hash_password(new_password)
    db.commit()
    return {"message": "Пароль успішно змінено"}
