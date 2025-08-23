# services/admin_service/schemas/admin_schemas.py
from __future__ import annotations
from datetime import datetime
from enum import Enum
from typing import Optional, List

from pydantic import BaseModel, EmailStr, Field, ConfigDict


# ---------- Базовые перечисления ----------
class AdminRole(str, Enum):
    superadmin = "superadmin"
    admin = "admin"
    moderator = "moderator"
    viewer = "viewer"


# ---------- Универсальные ответы ----------
class ErrorResponse(BaseModel):
    code: str = Field(..., description="Ключ ошибки (например, DUPLICATE_USERNAME)")
    message: str = Field(..., description="Человекочитаемое описание ошибки")
    details: Optional[dict] = Field(default=None, description="Доп. данные, если есть")


class PageMeta(BaseModel):
    page: int = 1
    page_size: int = 50
    total: int = 0


class PageResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")
    meta: PageMeta
    # data: List[T] - заполняется в конкретных роутах типизировано


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


# ---------- Пользователь админки ----------
class AdminUserBase(BaseModel):
    email: EmailStr
    username: str
    subscription_status: bool = False
    role: AdminRole = AdminRole.admin
    is_active: bool = True


class AdminUserOut(AdminUserBase):
    id: int
    date_registration: Optional[datetime] = None
    last_login_date: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class AdminUserCreate(AdminUserBase):
    password: str = Field(min_length=6, description="Пароль для администратора")


class AdminUserUpdate(BaseModel):
    """
    Частичное обновление (PATCH): все поля необязательные.
    """
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    subscription_status: Optional[bool] = None
    role: Optional[AdminRole] = None
    is_active: Optional[bool] = None


class AdminPasswordChange(BaseModel):
    old_password: str
    new_password: str = Field(min_length=6)


# ---------- Короткие вспомогательные модели ----------
class UserShort(BaseModel):
    id: int
    login: str

    model_config = ConfigDict(from_attributes=True)


# ---------- Аналитика / статистика ----------
class RevenueBreakdown(BaseModel):
    total: float = 0.0
    last_7_days: float = 0.0
    last_30_days: float = 0.0


class AdminStats(BaseModel):
    upload_count: int
    users_count: int
    revenue: RevenueBreakdown


# ---------- Коллекции / пагинация ----------
class AdminUsersPage(PageResponse):
    data: List[AdminUserOut]


# ---------- Фильтры для поиска/листа ----------
class AdminUserFilter(BaseModel):
    """
    Можно использовать как body для POST /admin/search
    или распарсить как query-параметры.
    """
    email: Optional[str] = None
    username: Optional[str] = None
    role: Optional[AdminRole] = None
    is_active: Optional[bool] = None
    subscription_status: Optional[bool] = None

    page: int = 1
    page_size: int = 50
    order_by: Optional[str] = Field(default="-date_registration",
                                    description="Поле сортировки, '-' для DESC")
