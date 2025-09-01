# services/auth_service/routers/profile.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from common.db.session import get_db
from common.models.user import User
from services.auth_service.schemas.user import UserOut
from common.api.auth_deps import get_current_user_id

# Нужен UserAuth (токен, который вернул /login)
router = APIRouter(prefix="", tags=["profile"])

@router.get("/me", response_model=UserOut)
def me(db: Session = Depends(get_db), user_id: int = Depends(get_current_user_id)):
    u = db.query(User).filter(User.id == user_id).first()
    if not u:
        raise HTTPException(status_code=404, detail="Користувача не знайдено")
    return UserOut.model_validate(u)
