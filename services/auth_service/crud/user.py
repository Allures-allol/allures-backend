# services/auth_service/crud/user.py
from sqlalchemy.orm import Session
from fastapi import HTTPException
from sqlalchemy import func

from common.models.user import User
from services.auth_service.utils.security import hash_password, verify_password

def get_all_users(db: Session, limit: int = 100, offset: int = 0):
    return db.query(User).order_by(User.id.asc()).limit(limit).offset(offset).all()

def delete_user_by_id(db: Session, user_id: int) -> bool:
    u = db.query(User).filter(User.id == user_id).first()
    if not u:
        return False
    db.delete(u)
    db.commit()
    return True

# (опционально, если где-то используешь)
def find_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(func.lower(func.btrim(User.email)) == (email or "").strip().lower()).first()
