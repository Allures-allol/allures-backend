from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from services.auth_service.schemas.user import UserProfileOut
from common.models.user import User
from services.auth_service.deps.auth import get_current_user
from common.db.session import get_db

router = APIRouter(
    prefix="/profile",
    tags=["profile"],
    dependencies=[Depends(get_current_user)]
)

@router.get("/me", response_model=UserProfileOut)
def me(current_user: User = Depends(get_current_user)):
    return current_user
