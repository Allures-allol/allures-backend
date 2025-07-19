# services/admin_service/schemas/admin_schemas.py
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional


class AdminLogin(BaseModel):
    email: EmailStr
    password: str


class AdminUserBase(BaseModel):
    email: EmailStr
    username: str
    subscription_status: Optional[bool] = False  # Вот здесь тип boolean (а не str)


class AdminUserOut(AdminUserBase):  # Наследуется от AdminUserBase
    id: int
    date_registration: Optional[datetime] = None
    last_login_date: Optional[datetime] = None

    class Config:
        from_attributes = True  # Поддержка SQLAlchemy-моделей

class AdminUserCreate(AdminUserBase):
    password: str

# Краткая информация о пользователе (может пригодиться для отзывов или аналитики)
class UserShort(BaseModel):
    id: int
    login: str

    class Config:
        from_attributes = True

# Статистика администратора / платформы
class AdminStats(BaseModel):
    upload_count: int
    users_count: int
    revenue_total: float

    class Config:
        from_attributes = True