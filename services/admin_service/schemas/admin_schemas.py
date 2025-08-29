# services/admin_service/schemas/admin_schemas.py
from __future__ import annotations
from datetime import datetime
from enum import Enum
from typing import Optional, List

from pydantic import BaseModel, EmailStr, Field, ConfigDict


# ---------- Базовые перечисления ----------
class AdminRole(str, Enum):
    owner = "owner"
    superadmin = "superadmin"
    admin = "admin"
    moderator = "moderator"
    viewer = "viewer"


# ---------- Универсальные ответы ----------
class ErrorResponse(BaseModel):
    code: str = Field(..., description="Ключ ошибки (например, DUPLICATE_USERNAME)")
    message: str = Field(..., description="Читаемое описание ошибки")
    details: Optional[dict] = Field(default=None, description="Доп. данные, если есть")


class PageMeta(BaseModel):
    page: int = 1
    page_size: int = 50
    total: int = 0


# ---------- Аутентификация ----------
class AdminLogin(BaseModel):
    email: EmailStr
    password: str


class TokenPair(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    expires_in: Optional[int] = Field(default=None, description="TTL access-токена в секундах")


class AdminLoginResponse(BaseModel):
    user_id: int
    email: EmailStr
    username: str
    role: AdminRole = AdminRole.admin
    tokens: TokenPair

# ---------- Пагинация ----------
class PageMeta(BaseModel):
    page: int = 1
    page_size: int = 50
    total: int = 0

class PageResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")
    meta: PageMeta

# ---------- Пользователь админки ----------
class AdminUserBase(BaseModel):
    email: EmailStr
    username: str
    subscription_status: bool = False
    role: AdminRole = AdminRole.admin
    is_active: bool = True

    # ↓ новые свойства (необязательные)
    subscription_code: Optional[str] = None
    subscription_language: Optional[str] = None
    subscription_name: Optional[str] = None

class AdminUserCreate(AdminUserBase):
    password: str = Field(min_length=6)

class AdminUserOut(AdminUserBase):
    id: int
    date_registration: Optional[datetime] = None
    last_login_date: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class AdminUserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    subscription_status: Optional[bool] = None
    role: Optional[AdminRole] = None
    is_active: Optional[bool] = None

    subscription_code: Optional[str] = None
    subscription_language: Optional[str] = None
    subscription_name: Optional[str] = None


class AdminPasswordChange(BaseModel):
    old_password: str
    new_password: str = Field(min_length=6)


# ---------- Коллекции / пагинация ----------
class AdminUsersPage(PageResponse):
    data: List[AdminUserOut]


# ---------- Фильтры для поиска/листа (уменьшенная версия) ----------
class AdminUserFilter(BaseModel):
    email: Optional[str] = None
    username: Optional[str] = None
    role: Optional[AdminRole] = None
    is_active: Optional[bool] = None
    subscription_status: Optional[bool] = None

    # новые поля фильтра
    subscription_code: Optional[str] = None
    subscription_language: Optional[str] = None
    subscription_name: Optional[str] = None

    page: int = 1
    page_size: int = 50
    order_by: Optional[str] = "-date_registration"
