# services/auth_service/crud/user.py
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from common.models.user import User
from services.auth_service.utils.security import hash_password, verify_password
from services.auth_service.schemas.user import UserCreate

def create_user(db: Session, user: UserCreate):
    db_user = User(login=user.login, password=hash_password(user.password))
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="User with this login already exists")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")

def authenticate_user(db: Session, login: str, password: str):
    user = db.query(User).filter(User.login == login).first()
    if user and verify_password(password, user.password):
        return user
    return None

def get_all_users(db: Session):
    return db.query(User).all()

def forgot_password(db: Session, email: str):
    user = db.query(User).filter(User.login == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": f"Password reset link sent to {email}"}

def reset_password(db: Session, email: str, new_password: str):
    user = db.query(User).filter(User.login == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.password = hash_password(new_password)
    db.commit()
    return {"message": "Password reset successful"}



