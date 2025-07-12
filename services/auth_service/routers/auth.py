# services/auth_service/routers/auth.py
from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session
from typing import List

from services.auth_service.schemas.user import (
    UserCreate, ForgotPassword, ResetPassword, UserOut,
    LoginRequest, LoginResponse, UserProfileUpdate
)
from services.auth_service.crud.user import (
    create_user, authenticate_user, forgot_password,
    reset_password, get_all_users, delete_user_by_id
)
from common.db.session import get_db
from common.models.user import User
from services.auth_service.utils.security import create_access_token

router = APIRouter()

@router.post("/register", response_model=UserOut)
def register(user: UserCreate, db: Session = Depends(get_db)):
    return create_user(db, user)

@router.post("/login", response_model=LoginResponse)
def login(user: LoginRequest, db: Session = Depends(get_db)):
    user_obj = authenticate_user(db, user.login, user.password)
    token = create_access_token(user_obj.login)

    return LoginResponse(
        access_token=token,
        token_type="bearer",
        id=user_obj.id,
        login=user_obj.login,
        role=user_obj.role,
        registered_at=user_obj.registered_at,
        is_blocked=user_obj.is_blocked
    )

@router.post("/forgot-password")
def forgot(user: ForgotPassword, db: Session = Depends(get_db)):
    return forgot_password(db, user.email)

@router.post("/reset-password")
def reset(user: ResetPassword, db: Session = Depends(get_db)):
    return reset_password(db, user.email, user.new_password)

@router.get("/users", response_model=List[UserOut])
def list_users(db: Session = Depends(get_db)):
    return get_all_users(db)

@router.get("/users/{user_id}", response_model=UserOut)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Користувача не знайдено")
    return user

@router.patch("/users/{user_id}", summary="Оновити дані користувача")
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

@router.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    success = delete_user_by_id(db, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Користувача не знайдено або вже видалено")
    return {"message": f"Користувач {user_id} успішно видалений"}
