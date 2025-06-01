# services/auth_service/routers/auth
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from services.auth_service.schemas.user import UserCreate, ForgotPassword, ResetPassword, UserOut
from services.auth_service.crud.user import create_user, authenticate_user, forgot_password, reset_password, get_all_users
from common.db.session import get_db
from services.auth_service.utils.security import create_access_token
from typing import List

router = APIRouter()

@router.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    return create_user(db, user)

@router.post("/login")
def login(user: UserCreate, db: Session = Depends(get_db)):
    user_obj = authenticate_user(db, user.login, user.password)
    if not user_obj:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token(user.login)
    return {"access_token": token, "token_type": "bearer"}

@router.post("/forgot-password")
def forgot(user: ForgotPassword, db: Session = Depends(get_db)):
    return forgot_password(db, user.email)

@router.post("/reset-password")
def reset(user: ResetPassword, db: Session = Depends(get_db)):
    return reset_password(db, user.email, user.new_password)

@router.get("/users", response_model=List[UserOut])
def list_users(db: Session = Depends(get_db)):
    return get_all_users(db)
