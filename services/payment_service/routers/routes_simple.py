# services/payment_service/routers/routes_simple.py
from __future__ import annotations

import os
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from common.db.session import get_db
from common.models.payment import Payment
from services.payment_service.schemas.simple import SimplePaymentCreate, SimplePaymentOut
from services.payment_service.crud.monobank import monobank_create_invoice
from common.config.settings import settings

router = APIRouter()


def _has_col(model, name: str) -> bool:
    """
    Безопасно проверяем, есть ли у ORM-модели колонка с указанным именем.
    Чтобы не падать, если схема Payment чуть отличается на проде/локале.
    """
    try:
        return hasattr(model, name) and name in model.__table__.columns
    except Exception:
        return False


def _set_if_exists(obj, **fields):
    """
    Проставляем только те поля, которые реально существуют у модели.
    """
    for k, v in fields.items():
        if _has_col(type(obj), k):
            setattr(obj, k, v)


@router.post(
    "/create-simple",
    response_model=SimplePaymentOut,
    summary="Создать простой платёж (Monobank) без привязок к user/company/subscription"
)
async def create_simple_payment(
    data: SimplePaymentCreate,
    db: Session = Depends(get_db),
):
    """
    1) Пытаемся создать инвойс в Monobank (если настроен токен).
    2) Если токена нет или включён MOCK-режим — генерим фейковые pageUrl/invoiceId локально.
    3) Создаём запись в payments только с базовыми полями (без FK).
    4) Возвращаем минимальный ответ фронту.

    ENV для мок-режима:
      - PAYMENT_MOCK=1  (форсит mock)
      - или отсутствие MONOBANK_TOKEN тоже включает mock.
    """
    # --- Решаем: реальный Monobank или mock ---
    mock_mode = os.getenv("PAYMENT_MOCK", "0") == "1" or not settings.MONOBANK_TOKEN

    if mock_mode:
        # Генерим локальные значения
        invoice_id = f"AUTO-{uuid.uuid4().hex[:12]}"
        page_url = f"https://pay.monobank.ua/{invoice_id}"
        status_val = "pending"
    else:
        # Реальный вызов Monobank
        try:
            # Monobank внутри всё равно требует reference/order_id — сделаем внутренний,
            # но наружу его не возвращаем и ни к чему не привязываем.
            internal_ref = f"SIMPLE-{uuid.uuid4().hex[:10].upper()}"
            mono = await monobank_create_invoice(
                amount_uah=float(data.amount_uah),
                order_id=internal_ref,
                email=data.email,
            )
            page_url = mono["pageUrl"]
            invoice_id = mono["invoiceId"]
            status_val = "pending"
        except Exception as e:
            # Пробрасываем читаемую ошибку наружу
            raise HTTPException(status_code=502, detail=f"Monobank error: {e}")

    # --- Сохраняем локальный payment с минимальным набором полей ---
    payment = Payment()

    # Стабильные поля (практически всегда есть)
    _set_if_exists(payment,
        provider="monobank",
        provider_invoice_id=invoice_id,
        payment_url=page_url,
        amount=float(data.amount_uah),
        currency=data.currency or "UAH",
        status=status_val,
        description=data.description,
    )

    # Мягкие поля — только если они реально присутствуют в модели
    _set_if_exists(payment,
        # Эти поля не используем в simple, но если колонки есть — пусть пишутся None
        user_id=None,
        company_id=None,
        subscription_id=None,
        product_id=None,
        category_id=None,
        # Доп. мета
        tariff=data.tariff,
        language=data.language,
        # Если у модели есть поле email
        email=data.email if hasattr(Payment, "email") else None,
        # Некоторые схемы имеют order_id — запишем внутренний ref, если колонка есть
        order_id=f"SIMPLE-{uuid.uuid4().hex[:8].upper()}" if _has_col(Payment, "order_id") else None,
    )

    db.add(payment)
    db.commit()
    db.refresh(payment)

    # --- Ответ фронту ---
    return SimplePaymentOut(
        pageUrl=page_url,
        invoiceId=invoice_id,
        status=status_val,
        amount=float(getattr(payment, "amount", data.amount_uah)),
        currency=getattr(payment, "currency", data.currency or "UAH"),
        description=getattr(payment, "description", data.description),
    )
