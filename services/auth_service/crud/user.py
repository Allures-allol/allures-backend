from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from common.models.user import User
from services.auth_service.utils.security import hash_password, verify_password
from services.auth_service.schemas.user import UserCreate


# ✅ Регистрация пользователя
def create_user(db: Session, user: UserCreate):
    db_user = User(login=user.login, password=hash_password(user.password))
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


# ✅ Аутентификация пользователя (вход)
def authenticate_user(db: Session, login: str, password: str):
    user = db.query(User).filter(User.login == login).first()

    if not user:
        raise HTTPException(status_code=404, detail="Користувача не знайдено")

    if user.is_blocked:
        raise HTTPException(status_code=403, detail="Акаунт заблоковано")

    if not verify_password(password, user.password):
        raise HTTPException(status_code=401, detail="Невірний пароль")

    return user


# ✅ Получить всех пользователей
def get_all_users(db: Session):
    return db.query(User).all()


# ✅ Запрос на сброс пароля
def forgot_password(db: Session, email: str):
    user = db.query(User).filter(User.login == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Користувача не знайдено")

    # Здесь может быть логика отправки email
    return {"message": f"Лист для скидання пароля надіслано на {email}"}


# ✅ Сброс пароля
def reset_password(db: Session, email: str, new_password: str):
    user = db.query(User).filter(User.login == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Користувача не знайдено")

    user.password = hash_password(new_password)
    db.commit()
    return {"message": "Пароль успішно змінено"}
