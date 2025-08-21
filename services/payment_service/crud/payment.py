# services/payment_service/crud/payment.py
from __future__ import annotations
from typing import Any, Dict, List, Optional
from decimal import Decimal
import httpx
from sqlalchemy.orm import Session
from sqlalchemy import select
from common.config.settings import settings
from common.models.payment import Payment

def create_payment(db: Session, data) -> Payment:
    obj = Payment(**data.dict())
    db.add(obj); db.commit(); db.refresh(obj)
    return obj

def get_all_payments(db: Session) -> List[Payment]:
    return db.query(Payment).all()

def get_payment_by_id(db: Session, payment_id: int) -> Optional[Payment]:
    return db.get(Payment, payment_id)

def get_payments_by_user(db: Session, user_id: int) -> List[Payment]:
    return db.execute(select(Payment).where(Payment.user_id == user_id)).scalars().all()

async def create_nowpayment_invoice(payload: Dict[str, Any]) -> Dict[str, Any]:
    api_key = settings.NOWPAYMENTS_API_KEY
    if not api_key:
        raise RuntimeError("NOWPAYMENTS_API_KEY is not set")
    url = "https://api.nowpayments.io/v1/invoice"
    headers = {"x-api-key": api_key}

    data = dict(payload)
    if "price_currency" in data and isinstance(data["price_currency"], str):
        data["price_currency"] = data["price_currency"].upper()
    if "pay_currency" in data and isinstance(data["pay_currency"], str):
        data["pay_currency"] = data["pay_currency"].lower()
    if isinstance(data.get("price_amount"), Decimal):
        data["price_amount"] = float(data["price_amount"])

    async with httpx.AsyncClient(timeout=httpx.Timeout(15.0)) as c:
        r = await c.post(url, json=data, headers=headers)
        r.raise_for_status()
        return r.json()
