# services/payment_service/schemas/simple.py
from __future__ import annotations

from typing import Any, Optional, Dict
from pydantic import BaseModel, ConfigDict, EmailStr, Field, PositiveFloat


class SimplePaymentCreate(BaseModel):
    """
    Упрощённый ввод для создания платежа.
    НИ ОДНОГО внешнего ключа и никаких order_id.
    """
    amount_uah: PositiveFloat = Field(..., description="Сумма в гривнах")
    currency: str = Field("UAH", min_length=3, max_length=10, description="Код валюты (по умолчанию UAH)")
    email: Optional[EmailStr] = Field(None, description="Email плательщика (опционально)")
    description: Optional[str] = Field(None, description="Описание платежа (отображается клиенту)")
    language: Optional[str] = Field(None, description="uk|ru|en — без жёсткой валидации")
    tariff: Optional[str] = Field(None, description="Любая метка тарифа/плана, не связана с БД")
    display_type: Optional[str] = Field("iframe", description="Подсказка фронту: iframe|redirect")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Произвольный JSON, если нужно")

    model_config = ConfigDict(
        extra="ignore",
        json_schema_extra={
            "examples": [
                {
                    "amount_uah": 1,
                    "currency": "UAH",
                    "email": "user@example.com",
                    "description": "Тестовый платёж 1 грн"
                },
                {
                    "amount_uah": 99,
                    "currency": "UAH",
                    "email": "pro@example.com",
                    "description": "Подписка Pro на месяц",
                    "language": "uk",
                    "tariff": "pro",
                    "display_type": "iframe"
                },
                {
                    "amount_uah": 1700,
                    "currency": "UAH",
                    "email": "vip@example.com",
                    "description": "Оплата VIP тарифа",
                    "tariff": "vip",
                    "language": "ru",
                    "metadata": {"campaign": "september_promo", "user_segment": "loyal"}
                }
            ]
        },
    )


class SimplePaymentOut(BaseModel):
    """
    Минимальный ответ фронту — готовая ссылка и ID инвойса.
    """
    pageUrl: str
    invoiceId: str
    status: str
    amount: float
    currency: str
    description: Optional[str] = None
