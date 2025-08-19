# services/subscription_service/schemas/subscription_schemas.py
from pydantic import BaseModel
from datetime import datetime
from enum import Enum
from typing import Optional

# Базовая схема (без id, используется в create/update)
class SubscriptionBase(BaseModel):
    code: str
    language: str
    name: str
    price: int
    duration_days: int
    product_limit: int
    promo_balance: int
    support_level: Optional[str]
    stats_access: bool
    description: Optional[str]

# Подписка из БД
class SubscriptionOut(SubscriptionBase):
    id: int

    class Config:
        from_attributes = True

# Статус подписки
class SubscriptionStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


# Запрос на обновление подписки
class UpdateSubscriptionRequest(BaseModel):
    login: str
    new_status: SubscriptionStatus

# Подписка пользователя
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
