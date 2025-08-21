# services/subscription_service/schemas/subscription_schemas.py
from __future__ import annotations

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from enum import Enum

# ---------- Subscription ----------

class SubscriptionBase(BaseModel):
    code: str
    language: str
    name: str
    price: int
    duration_days: int
    product_limit: int
    promo_balance: int
    support_level: Optional[str] = None
    stats_access: bool
    description: Optional[str] = None

class SubscriptionOut(SubscriptionBase):
    id: int
    model_config = ConfigDict(from_attributes=True)  # Pydantic v2

class SubscriptionStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"

# ---------- UserSubscription ----------

class UserSubscriptionOut(BaseModel):
    id: int
    user_id: int
    subscription_id: int
    start_date: datetime
    end_date: datetime
    is_active: bool
    auto_renew: bool
    payment_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)
