# services/payment_service/routers/payment.py
from __future__ import annotations
from typing import List

from fastapi import APIRouter, Depends, Request, Header, HTTPException
from sqlalchemy.orm import Session
import httpx

from sqlalchemy import text as sqla_text
import traceback

from common.db.session import get_db
from common.config.settings import settings
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from decimal import Decimal

from services.payment_service.schemas.payment import PaymentCreate, PaymentOut
from services.payment_service.crud.payment import (
    create_payment,
    get_all_payments,
    get_payment_by_id,
    get_payments_by_user,
    create_nowpayment_invoice,
)

from services.payment_service.schemas.monobank import MonoCreateInvoiceIn, MonoCreateInvoiceOut
from services.payment_service.crud.monobank import monobank_create_invoice, verify_monobank_signature
from services.payment_service.schemas.payment import PaymentCreate
from services.payment_service.crud.payment import create_payment

router = APIRouter(tags=["payments"])

class NowPaymentRequest(BaseModel):
    user_id: int = Field(..., ge=1)
    amount: Decimal = Field(..., gt=0)
    currency: str = "USD"
    pay_currency: str = "BTC"
    order_description: str = "Test order"

#  список всех платежей
@router.get("/", response_model=List[PaymentOut])
def list_payments(db: Session = Depends(get_db)):
    return get_all_payments(db)

#  получить один платёж по id
@router.get("/{payment_id}", response_model=PaymentOut)
def get_payment(payment_id: int, db: Session = Depends(get_db)):
    obj = get_payment_by_id(db, payment_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Payment not found")
    return obj

#  получить платежи по user_id
@router.get("/users/{user_id}/payments", response_model=List[PaymentOut])
def list_user_payments(user_id: int, db: Session = Depends(get_db)):
    return get_payments_by_user(db, user_id)


# ----- Monobank: create -----
@router.post("/monobank/create", response_model=MonoCreateInvoiceOut)
async def monobank_create(data: MonoCreateInvoiceIn, db: Session = Depends(get_db)):
    try:
        res = await monobank_create_invoice(
            amount_uah=data.amount_uah,
            order_id=data.order_id,
            email=data.email,
            display_type=data.display_type,
        )

        created = create_payment(db, PaymentCreate(
            user_id = data.user_id or 1,
            subscription_id = data.subscription_id,          # ← сохраняем
            amount = data.amount_uah,
            status = "pending",
            payment_url = res["pageUrl"],
            provider = "monobank",
            provider_invoice_id = res["invoiceId"],
        ))

        return MonoCreateInvoiceOut(
            pageUrl = res["pageUrl"],
            invoiceId = res["invoiceId"],
            status = "pending",
            amount = float(data.amount_uah),
            user_id = data.user_id,
            subscription_id = data.subscription_id,          # ← возвращаем
        )

    except (httpx.HTTPStatusError, RuntimeError) as e:
        raise HTTPException(status_code=502, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Monobank create failed: {e}")
# ----- Monobank: webhook -----
@router.post("/monobank/webhook")
async def monobank_webhook(
    request: Request,
    db: Session = Depends(get_db),
    x_signature: str | None = Header(default=None, alias="X-Signature"),
):
    raw = await request.body()
    sig_ok = verify_monobank_signature(raw, x_signature)

    try:
        payload = await request.json()
    except Exception:
        payload = {}

    status_raw = (payload.get("status") or payload.get("paymentStatus") or "").lower()
    invoice_id = payload.get("invoiceId") or payload.get("invoice_id")

    # если хочешь оставить как работало – ок:
    if status_raw in {"success", "approved", "holded"}:
        amount_cop = int(payload.get("amount", 0))
        amount = amount_cop / 100.0
        # create_payment(db, PaymentCreate(
        #     user_id=1,
        #     amount=amount,
        #     status="paid",
        #     payment_url=None,
        #     # provider="monobank",
        #     # provider_invoice_id=invoice_id,
        # ))

    return {
        "status": "ok",
        "signature_ok": sig_ok,
        "invoiceId": invoice_id,
        "status_raw": status_raw,
    }

@router.get("/__debug/env")
def dbg_env():
    from common.config.settings import settings
    return {
        "MAINDB_URL": settings.MAINDB_URL,
        "PAYMENT_SERVICE_URL": settings.PAYMENT_SERVICE_URL,
        "MONOBANK_TOKEN_set": bool(settings.MONOBANK_TOKEN),
        "MONOBANK_REDIRECT_URL": settings.MONOBANK_REDIRECT_URL,
        "MONOBANK_WEBHOOK_URL": settings.MONOBANK_WEBHOOK_URL,
    }

@router.post("/__debug/create-table")
def dbg_create_table(db: Session = Depends(get_db), text=None):
    sql = """
    CREATE TABLE IF NOT EXISTS payments (
        id                  SERIAL PRIMARY KEY,
        user_id             INT REFERENCES users(id),
        subscription_id     INT REFERENCES subscriptions(id),
        amount              NUMERIC(10,2) NOT NULL,
        status              VARCHAR(20) DEFAULT 'pending',
        payment_url         VARCHAR(255),
        provider            VARCHAR(20),
        provider_invoice_id VARCHAR(100),
        created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    CREATE INDEX IF NOT EXISTS idx_payments_user_id    ON payments(user_id);
    CREATE INDEX IF NOT EXISTS idx_payments_provider   ON payments(provider);
    CREATE INDEX IF NOT EXISTS idx_payments_invoice_id ON payments(provider_invoice_id);
    CREATE INDEX IF NOT EXISTS idx_payments_created_at ON payments(created_at);
    """
    db.execute(text(sql))
    db.commit()
    return {"ok": True}

@router.post("/__debug/bootstrap")
def dbg_bootstrap(db: Session = Depends(get_db)):
    try:
        sql = """
        CREATE TABLE IF NOT EXISTS payments (
            id                  SERIAL PRIMARY KEY,
            user_id             INT,
            subscription_id     INT,
            amount              NUMERIC(10,2) NOT NULL,
            status              VARCHAR(20) DEFAULT 'pending',
            payment_url         VARCHAR(255),
            provider            VARCHAR(20),
            provider_invoice_id VARCHAR(100),
            created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE INDEX IF NOT EXISTS idx_payments_user_id      ON payments(user_id);
        CREATE INDEX IF NOT EXISTS idx_payments_provider     ON payments(provider);
        CREATE INDEX IF NOT EXISTS idx_payments_invoice_id   ON payments(provider_invoice_id);
        CREATE INDEX IF NOT EXISTS idx_payments_created_at   ON payments(created_at);
        """
        db.execute(sqla_text(sql))
        db.commit()
        return {"ok": True}
    except Exception as e:
        return {"ok": False, "error": str(e), "traceback": traceback.format_exc()}

@router.post("/__debug/test-insert")
def dbg_insert(db: Session = Depends(get_db)):
    try:
        from services.payment_service.schemas.payment import PaymentCreate
        from services.payment_service.crud.payment import create_payment
        obj = create_payment(db, PaymentCreate(
            user_id=999,
            amount=123.45,
            status="pending",
            payment_url="https://example.com/debug",
            provider="debug",
            provider_invoice_id="DBG-123"
        ))
        return {"ok": True, "id": obj.id}
    except Exception as e:
        return {
            "ok": False,
            "error": str(e),
            "traceback": traceback.format_exc()
        }

# создать платёж (локально в БД)
@router.post("/", response_model=PaymentOut)
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

# вебхук (простой)
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
