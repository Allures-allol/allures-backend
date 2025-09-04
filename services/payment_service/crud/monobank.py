from __future__ import annotations

import base64
import hashlib
import hmac
from typing import Any, Dict, List, Optional

import httpx
from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from common.config.settings import settings
from common.models.payment import Payment

MONO_API_CREATE = "https://api.monobank.ua/api/merchant/invoice/create"


# -------------------------------
# CRUD для локальных платежей Monobank
# -------------------------------
def create_mono_invoice(db: Session, invoice: dict, page_url: str) -> Payment:
    """
    Создаёт локальную запись платежа (Monobank) в таблице payments.
    Ожидает, что в invoice уже есть поля user_id/company_id/subscription_id/... и amount_uah.
    """
    obj = Payment(
        user_id=invoice.get("user_id"),
        company_id=invoice.get("company_id"),
        subscription_id=invoice.get("subscription_id"),
        amount=invoice.get("amount_uah"),
        currency=invoice.get("currency") or "UAH",
        payment_url=page_url,
        provider_invoice_id=invoice.get("order_id"),
        provider="monobank",
        status="pending",
        tariff=invoice.get("tariff"),
        language=invoice.get("language"),
        description=invoice.get("description"),
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def update_payment_status(db: Session, invoice_id: str, status: str) -> Optional[Payment]:
    """
    Обновляет статус платежа по provider_invoice_id (invoiceId заказа Monobank).
    Возвращает обновлённый Payment или None, если не найден.
    """
    payment = (
        db.query(Payment)
        .filter(Payment.provider == "monobank", Payment.provider_invoice_id == invoice_id)
        .first()
    )
    if not payment:
        return None
    payment.status = status
    db.commit()
    db.refresh(payment)
    return payment


def get_payment_by_invoice_id(db: Session, invoice_id: str) -> Optional[Payment]:
    """
    Возвращает платеж Monobank по provider_invoice_id.
    """
    return (
        db.query(Payment)
        .filter(Payment.provider == "monobank", Payment.provider_invoice_id == invoice_id)
        .first()
    )


def get_payments_by_user(db: Session, user_id: int, company_id: Optional[int] = None) -> List[Payment]:
    """
    Возвращает платежи пользователя (опционально — в рамках company_id), провайдер Monobank.
    """
    q = db.query(Payment).filter(Payment.provider == "monobank", Payment.user_id == user_id)
    if company_id is not None:
        q = q.filter(Payment.company_id == company_id)
    return q.order_by(Payment.created_at.desc()).all()


def get_all_mono_payments(db: Session) -> List[Payment]:
    """
    Возвращает все платежи Monobank.
    """
    return (
        db.query(Payment)
        .filter(Payment.provider == "monobank")
        .order_by(Payment.created_at.desc())
        .all()
    )


def delete_payment(db: Session, payment_id: int) -> bool:
    """
    Удаляет платеж по его первичному ключу (id). Возвращает True/False.
    """
    res = db.execute(delete(Payment).where(Payment.id == payment_id))
    db.commit()
    return bool(res.rowcount)


def delete_payment_by_invoice_id(db: Session, invoice_id: str) -> bool:
    """
    Удаляет платеж Monobank по provider_invoice_id. Возвращает True/False.
    """
    res = db.execute(
        delete(Payment).where(
            Payment.provider == "monobank",
            Payment.provider_invoice_id == invoice_id,
        )
    )
    db.commit()
    return bool(res.rowcount)


# -------------------------------
# Monobank API Integration
# -------------------------------
async def monobank_create_invoice(*, amount_uah: float, order_id: str, email: Optional[str] = None) -> Dict[str, Any]:
    """
    Создаёт инвойс через API Monobank и возвращает {"pageUrl": ..., "invoiceId": ...}.
    """
    if not settings.MONOBANK_TOKEN:
        raise RuntimeError("MONOBANK_TOKEN is not set")

    amount_cop = int(round(amount_uah * 100))  # копейки
    body = {
        "amount": amount_cop,
        "ccy": 980,  # UAH
        "merchantPaymInfo": {
            "reference": order_id,
            "destination": f"Order {order_id}",
            "comment": f"Order {order_id}",
            "customerEmails": [email] if email else [],
            "redirectUrl": settings.MONOBANK_REDIRECT_URL,
            **({"webHookUrl": settings.MONOBANK_WEBHOOK_URL} if settings.MONOBANK_WEBHOOK_URL else {}),
        },
        "paymentType": "debit",
    }
    headers = {"X-Token": settings.MONOBANK_TOKEN, "Content-Type": "application/json"}

    async with httpx.AsyncClient(timeout=httpx.Timeout(20.0)) as client:
        r = await client.post(MONO_API_CREATE, json=body, headers=headers)
        r.raise_for_status()
        data = r.json()

    if not data.get("pageUrl") or not data.get("invoiceId"):
        raise RuntimeError(f"Monobank response missing fields: {data}")

    return {"pageUrl": data["pageUrl"], "invoiceId": data["invoiceId"]}


def verify_monobank_signature(raw_body: bytes, signature_b64: Optional[str]) -> bool:
    """
    Проверка подписи Monobank (X-Signature): HMAC-SHA256(body, MONOBANK_TOKEN), base64.
    """
    if not signature_b64 or not settings.MONOBANK_TOKEN:
        return False
    secret = settings.MONOBANK_TOKEN.encode("utf-8")
    mac = hmac.new(secret, msg=raw_body, digestmod=hashlib.sha256).digest()
    calc = base64.b64encode(mac).decode("utf-8")
    return hmac.compare_digest(calc, signature_b64)
