# services/auth_service/routers/user.py
from fastapi import APIRouter, Depends, HTTPException, Query, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os
from sqlalchemy.orm import Session

from common.db.session import get_db
from common.api.auth_deps import get_current_user
from common.models.user import User
from services.auth_service.schemas.user import UserOut
from services.auth_service.crud.user import (
    get_all_users,
    delete_user_by_id,
    find_user_by_email,
)

# отдельный замок в Swagger (для админских операций)
admin_scheme = HTTPBearer(
    description="Service Admin JWT",
    auto_error=False,
    scheme_name="AdminJWT",
)

def admin_guard(credentials: HTTPAuthorizationCredentials = Security(admin_scheme)):
    admin_jwt = os.getenv("ADMIN_JWT", "")
    if not admin_jwt:
        raise HTTPException(status_code=500, detail="ADMIN_JWT is not configured")
    if not credentials or not credentials.credentials:
        raise HTTPException(status_code=401, detail="Missing admin bearer token")
    if credentials.credentials != admin_jwt:
        raise HTTPException(status_code=403, detail="Invalid admin token")

router = APIRouter(tags=["users"])

# ---------- Публичные ручки (без токена, только для тестов/фронта) ----------
@router.get("/all", response_model=list[UserOut])
def list_users_public(
    db: Session = Depends(get_db),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
):
    """Вывести всех пользователей без авторизации (только для теста/фронта)."""
    return db.query(User).order_by(User.id.asc()).limit(limit).offset(offset).all()

@router.get("/by-email", response_model=UserOut)
def get_user_by_email_endpoint(
    email: str,
    db: Session = Depends(get_db),
    _=Security(admin_guard),
):
    u = find_user_by_email(db, email)
    if not u:
        raise HTTPException(status_code=404, detail="User not found")
    return u

@router.get("/{user_id:int}", response_model=UserOut)  # <= тип int в пути
def get_user_by_id_public(user_id: int, db: Session = Depends(get_db)):
    u = db.query(User).filter(User.id == user_id).first()
    if not u:
        raise HTTPException(status_code=404, detail="User not found")
    return u

# ---------- Админ-ручки (защищены токеном) ----------
@router.get("/", response_model=list[UserOut])
def list_users_admin(
    db: Session = Depends(get_db),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    _=Security(admin_guard),
):
    return db.query(User).order_by(User.id.asc()).limit(limit).offset(offset).all()

@router.delete("/{user_id:int}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    _=Security(admin_guard),
):
    ok = delete_user_by_id(db, user_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Користувача не знайдено або вже видалено")
    return {"message": f"Користувач {user_id} успішно видалений"}
