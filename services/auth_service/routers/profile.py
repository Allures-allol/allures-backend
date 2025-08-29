# services/auth_service/routers/profile.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from common.db.session import get_db
from common.models.user import User
from services.auth_service.schemas.user import UserOut

router = APIRouter(prefix="/profile", tags=["profile"])

@router.get("/me", response_model=UserOut)
def me(email: str = Query(..., description="DEV: передай email"), db: Session = Depends(get_db)):
    u = db.query(User).filter(func.lower(func.btrim(User.email)) == (email or "").strip().lower()).first()
    if not u:
        raise HTTPException(status_code=404, detail="Користувача не знайдено")
    if not u.is_email_confirmed:
        raise HTTPException(status_code=403, detail="Підтвердіть email")
    return u
