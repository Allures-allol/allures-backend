# services/payment_service/routers/payment.py
from __future__ import annotations
from typing import List
from fastapi import APIRouter, Depends, Request, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from decimal import Decimal

from common.config.settings import settings
from common.db.session import get_db
from services.payment_service.schemas.payment import PaymentCreate, PaymentOut
from services.payment_service.crud.payment import (
    create_payment,
    get_all_payments,
    get_payment_by_id,
    get_payments_by_user,
    create_nowpayment_invoice,
)

router = APIRouter()

class NowPaymentRequest(BaseModel):
    user_id: int = Field(..., ge=1)
    amount: Decimal = Field(..., gt=0)
    currency: str = "USD"
    pay_currency: str = "BTC"
    order_description: str = "Test order"

#  список всех платежей
@router.get("/payments", response_model=List[PaymentOut])
def list_payments(db: Session = Depends(get_db)):
    return get_all_payments(db)

#  получить один платёж по id
@router.get("/payments/{payment_id}", response_model=PaymentOut)
def get_payment(payment_id: int, db: Session = Depends(get_db)):
    obj = get_payment_by_id(db, payment_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Payment not found")
    return obj

#  получить платежи по user_id
@router.get("/users/{user_id}/payments", response_model=List[PaymentOut])
def list_user_payments(user_id: int, db: Session = Depends(get_db)):
    return get_payments_by_user(db, user_id)

# создать платёж (локально в БД)
@router.post("/payments", response_model=PaymentOut)
def create(data: PaymentCreate, db: Session = Depends(get_db)):
    return create_payment(db, data)

# создать инвойс у NowPayments
@router.post("/nowpayment/")
async def create_nowpayment(data: NowPaymentRequest):
    ipn = settings.NGROK_WEBHOOK_URL or (
        getattr(settings, "PAYMENTS_SERVICE_URL", "").rstrip("/") + "/payment/webhook"
        if getattr(settings, "PAYMENTS_SERVICE_URL", None) else None
    )

    payload = {
        "price_amount": data.amount,
        "price_currency": data.currency,
        "pay_currency": data.pay_currency,
        "order_description": data.order_description,
        "ipn_callback_url": ipn,
    }
    try:
        return await create_nowpayment_invoice(payload)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY,
                            detail=f"NowPayments error: {e}")

# вебхук (пока простой)
@router.post("/webhook")
async def payment_webhook(request: Request, db: Session = Depends(get_db)):
    try:
        data = await request.json()
        print(" Webhook received:", data)
        if (data.get("payment_status") or data.get("status") or "").lower() == "finished":
            amount = float(data.get("pay_amount") or data.get("price_amount") or 0)
            create_payment(db, PaymentCreate(user_id=1, amount=amount, status="paid", payment_url=None))
        return {"status": "ok"}
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=400)
