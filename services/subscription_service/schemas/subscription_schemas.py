# services/subscription_service/schemas/subscription_schemas.py
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


# --- Базовые перечисления/константы ---

class SubscriptionStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


# --- Схемы подписок ---

class SubscriptionBase(BaseModel):
    code: str = Field(..., description="Код тарифа (e.g. basic, advanced, premium, free)")
    language: str = Field(..., description="Язык записи (ru|uk|en)")
    name: str = Field(..., description="Человекочитаемое имя тарифа")
    price: int = Field(..., ge=0, description="Цена в минимальных единицах (например, копейки/центы)")
    duration_days: int = Field(..., ge=1, description="Срок действия в днях")
    product_limit: int = Field(..., ge=0, description="Лимит товаров/операций на период")
    promo_balance: int = Field(..., ge=0, description="Бонусный баланс/кредиты")
    support_level: Optional[str] = Field(None, description="Уровень поддержки, e.g. 'standard'|'priority'")
    stats_access: bool = Field(..., description="Доступ к расширенной статистике")
    description: Optional[str] = Field(None, description="Описание тарифа")

class SubscriptionOut(SubscriptionBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


# --- Схемы пользовательских подписок ---

class UserSubscriptionBase(BaseModel):
    user_id: int
    subscription_id: int
    is_active: bool
    auto_renew: bool

class UserSubscriptionOut(UserSubscriptionBase):
    id: int
    start_date: datetime
    end_date: datetime
    payment_id: Optional[int] = None

    # Опционально: в ответ можно включать информацию о тарифе (если делаешь joinedload)
    # subscription: Optional[SubscriptionOut] = None

    model_config = ConfigDict(from_attributes=True)


# --- Вспомогательные схемы для аналитики/статистики ---

class ActiveByPlanItem(BaseModel):
    code: str = Field(..., description="Код тарифа")
    count: int = Field(..., ge=0, description="Количество активных подписок с этим тарифом")

    model_config = ConfigDict(from_attributes=True)

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
