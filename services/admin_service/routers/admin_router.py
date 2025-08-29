# services/admin_service/routers/admin_router.py
from __future__ import annotations
import secrets

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
import httpx

from common.db.session import get_db
from common.config.settings import settings

from services.admin_service.schemas.admin_schemas import (
    AdminUserCreate,
    AdminUserOut,
    AdminLogin,
    AdminLoginResponse,
    TokenPair,
    AdminUsersPage,
    PageMeta,
    AdminUserUpdate,
    AdminPasswordChange,
    AdminUserFilter,
    ErrorResponse,
    AdminRole
)
from services.admin_service.crud import admin_crud
from services.admin_service.utils.security import verify_password

router = APIRouter(tags=["Admin"])

# --------- аккаунты админов ---------
@router.post("/create", response_model=AdminUserOut, responses={409: {"model": ErrorResponse}})
def create_admin(admin: AdminUserCreate, db: Session = Depends(get_db)):
    try:
        return admin_crud.create_admin_user(db, admin)
    except ValueError as e:
        code = str(e)
        if code in ("DUPLICATE_EMAIL", "DUPLICATE_USERNAME", "UNIQUE_VIOLATION"):
            raise HTTPException(status_code=409, detail={"code": code, "message": "Unique constraint violation"})
        raise

@router.post("/login", response_model=AdminLoginResponse, responses={401: {"model": ErrorResponse}})
def login_admin(credentials: AdminLogin, db: Session = Depends(get_db)):
    admin = admin_crud.get_admin_user_by_email(db, credentials.email)
    if not admin or not verify_password(credentials.password, admin.password_hash):
        raise HTTPException(status_code=401, detail={"code": "INVALID_CREDENTIALS", "message": "Неверный логин или пароль"})

    tokens = TokenPair(
        access_token=secrets.token_urlsafe(32),
        refresh_token=None,
        token_type="bearer",
        expires_in=3600,
    )
    return {
        "user_id": admin.id,
        "email": admin.email,
        "username": admin.username,
        "role": admin.role,
        "tokens": tokens,
    }

@router.get("/all", response_model=AdminUsersPage)
def get_all_admins(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),

    email: str | None = None,
    username: str | None = None,
    role: AdminRole | None = None,
    is_active: bool | None = None,
    subscription_status: bool | None = None,

    # новые query для фильтрации
    subscription_code: str | None = Query(None, description="exact match"),
    subscription_language: str | None = Query(None, description="exact match (uk|ru|en)"),
    subscription_name: str | None = Query(None, description="ILIKE %value%"),

    order_by: str | None = Query("-date_registration"),
):
    flt = AdminUserFilter(
        email=email,
        username=username,
        role=role,
        is_active=is_active,
        subscription_status=subscription_status,
        subscription_code=subscription_code,
        subscription_language=subscription_language,
        subscription_name=subscription_name,
        page=page,
        page_size=page_size,
        order_by=order_by,
    )
    data, total = admin_crud.list_admins(db, flt)
    return {"meta": PageMeta(page=page, page_size=page_size, total=total), "data": data}

@router.patch("/{admin_id}", response_model=AdminUserOut, responses={404: {"model": ErrorResponse}, 409: {"model": ErrorResponse}})
def update_admin(admin_id: int, patch: AdminUserUpdate, db: Session = Depends(get_db)):
    try:
        return admin_crud.update_admin_user(db, admin_id, patch)
    except LookupError:
        raise HTTPException(status_code=404, detail={"code": "NOT_FOUND", "message": "Админ не найден"})
    except ValueError as e:
        code = str(e)
        if code in ("DUPLICATE_EMAIL", "DUPLICATE_USERNAME", "UNIQUE_VIOLATION"):
            raise HTTPException(status_code=409, detail={"code": code, "message": "Unique constraint violation"})
        raise

@router.post("/{admin_id}/change-password", responses={404: {"model": ErrorResponse}, 403: {"model": ErrorResponse}})
def change_password(admin_id: int, body: AdminPasswordChange, db: Session = Depends(get_db)):
    try:
        admin_crud.change_admin_password(db, admin_id, body)
        return {"message": "Пароль изменён"}
    except LookupError:
        raise HTTPException(status_code=404, detail={"code": "NOT_FOUND", "message": "Админ не найден"})
    except PermissionError:
        raise HTTPException(status_code=403, detail={"code": "BAD_OLD_PASSWORD", "message": "Старый пароль неверен"})

# --------- статистика / подписки ---------
@router.get("/{admin_id}/stats")
def get_admin_stats(admin_id: int, db: Session = Depends(get_db)):
    return admin_crud.get_admin_stats(db)

def _subscription_base() -> str:
    return (settings.SUBSCRIPTION_SERVICE_URL or "").rstrip("/")

@router.post("/activate-subscription")
async def activate_subscription(user_id: int, payment_id: int):
    base = _subscription_base()
    if not base:
        raise HTTPException(status_code=500, detail="SUBSCRIPTION_SERVICE_URL is not set")

    # если base уже заканчивается на /subscription — не дублируем
    path = "/activate-subscription" if base.endswith("/subscription") else "/subscription/activate-subscription"
    url = f"{base}{path}"

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.post(url, params={"user_id": user_id, "payment_id": payment_id})
    except httpx.RequestError:
        raise HTTPException(status_code=502, detail="Subscription service unreachable: request failed")

    if resp.status_code >= 400:
        ct = resp.headers.get("content-type", "")
        raise HTTPException(status_code=resp.status_code, detail=resp.json() if ct.startswith("application/json") else resp.text)

    return resp.json()
