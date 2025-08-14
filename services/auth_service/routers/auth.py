# services/auth_service/routers/auth.py
from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session
from typing import List

from services.auth_service.schemas.user import (
    UserCreate, ForgotPassword, ResetPassword, UserOut,
    LoginRequest, LoginResponse, UserProfileOut, UserProfileUpdate
)
from services.auth_service.crud.user import (
    create_user, authenticate_user, forgot_password,
    reset_password, get_all_users, delete_user_by_id
)
from services.auth_service.utils.security import hash_password, create_access_token
from common.db.session import get_db
from common.models.user import User
from services.auth_service.deps.auth import get_current_user

router = APIRouter()


# --- Регистрация ---
@router.post("/register", response_model=UserOut)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    hashed_pw = hash_password(user.password)
    db_user = User(
        login=user.login,
        password=hashed_pw
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


# --- Логин ---
@router.post("/login", response_model=LoginResponse)
def login(user: LoginRequest, db: Session = Depends(get_db)):
    user_obj = authenticate_user(db, user.login, user.password)
    token = create_access_token(user_obj.id, user_obj.login, user_obj.role)

    return LoginResponse(
        access_token=token,
        token_type="bearer",
        id=user_obj.id,
        login=user_obj.login,
        role=user_obj.role,
        registered_at=user_obj.registered_at,
        is_blocked=user_obj.is_blocked
    )


# --- Получение текущего профиля ---
@router.get("/me", response_model=UserOut)
def get_profile_me(current_user: User = Depends(get_current_user)):
    return current_user

# --- Сброс пароля ---
@router.post("/forgot-password")
def forgot(user: ForgotPassword, db: Session = Depends(get_db)):
    return forgot_password(db, user.email)


@router.post("/reset-password")
def reset(user: ResetPassword, db: Session = Depends(get_db)):
    return reset_password(db, user.email, user.new_password)


# --- Список всех пользователей (только для админа позже) ---
@router.get("/users", response_model=List[UserOut], dependencies=[Depends(get_current_user)])
def list_users(db: Session = Depends(get_db)):
    return get_all_users(db)


# --- Получение пользователя по ID ---
@router.get("/users/{user_id}", response_model=UserOut, dependencies=[Depends(get_current_user)])
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Користувача не знайдено")
    return user


# --- Обновление профиля пользователя ---
@router.patch("/users/{user_id}", summary="Оновити дані користувача", dependencies=[Depends(get_current_user)])
def patch_user_profile(
    user_id: int,
    profile_data: UserProfileUpdate,
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Користувача не знайдено")

    for field, value in profile_data.dict(exclude_unset=True).items():
        setattr(user, field, value)

    db.commit()
    db.refresh(user)
    return {"message": "Профіль оновлено", "user_id": user_id}


# --- Удаление пользователя ---
@router.delete("/users/{user_id}", dependencies=[Depends(get_current_user)])
def delete_user(user_id: int, db: Session = Depends(get_db)):
    success = delete_user_by_id(db, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Користувача не знайдено або вже видалено")
    return {"message": f"Користувач {user_id} успішно видалений"}
