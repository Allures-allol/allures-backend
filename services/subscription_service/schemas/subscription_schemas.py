# services/subscription_service/schemas/subscription_schemas.py
from pydantic import BaseModel
from datetime import datetime
from enum import Enum
from typing import Optional

# Базовая модель подписки
class SubscriptionBase(BaseModel):
    name: str
    price: int
    duration_days: int
    product_limit: int
    promo_balance: int
    support_level: str
    stats_access: bool
    description: Optional[str] = None

# Подписка (чтение из БД)
class SubscriptionOut(SubscriptionBase):
    id: int

    class Config:
        from_attributes = True

# Статус подписки (опционально)
class SubscriptionStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"

# Запрос на обновление подписки
class UpdateSubscriptionRequest(BaseModel):
    login: str
    new_status: SubscriptionStatus

# Модель для вывода подписки пользователя
class UserSubscriptionOut(BaseModel):
    id: int
    user_id: int
    subscription_id: int
    start_date: datetime
    end_date: datetime
    is_active: bool
    subscription: SubscriptionOut

    class Config:
        from_attributes = True
