# services/auth_service/crud/user.py
from sqlalchemy.orm import Session
from common.models.user import User
from services.auth_service.utils.security import hash_password, verify_password
from services.auth_service.schemas.user import UserCreate

def create_user(db: Session, user: UserCreate):
    db_user = User(login=user.login, password=hash_password(user.password))
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(db: Session, login: str, password: str):
    user = db.query(User).filter(User.login == login).first()
    if user and verify_password(password, user.password):
        return user
    return None

