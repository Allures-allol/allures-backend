# services/auth_service/crud/user.py

from sqlalchemy.orm import Session
from sqlalchemy import func
from common.models.user import User

def get_all_users(db: Session, limit: int = 100, offset: int = 0):
    return (
        db.query(User)
        .order_by(User.id.asc())
        .limit(limit)
        .offset(offset)
        .all()
    )

def delete_user_by_id(db: Session, user_id: int) -> bool:
    u = db.query(User).filter(User.id == user_id).first()
    if not u:
        return False
    db.delete(u)
    db.commit()
    return True

def find_user_by_email(db: Session, email: str) -> User | None:
    email_norm = (email or "").strip().lower()
    return (
        db.query(User)
        .filter(func.lower(func.btrim(User.email)) == email_norm)
        .first()
    )
