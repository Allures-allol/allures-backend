# services/auth_service/routers/profile.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from common.db.session import get_db
from common.models.user import User
from services.auth_service.schemas.user import UserOut
from common.api.auth_deps import get_current_user

# Нужен UserAuth (токен, который вернул /login)
router = APIRouter(prefix="", tags=["profile"])

@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)):
    return UserOut.model_validate(user)
