# services/payment_service/routers/public_history_router.py
from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text as sqla_text

from common.db.session import get_db
from common.models.payment import Payment
from services.payment_service.crud.payment import get_all_payments
from services.payment_service.schemas.public import PaymentOut, OrderOut

router = APIRouter()

# Пытаемся использовать реальную таблицу orders (1:1 с payments)
try:
    from common.models.order import Order  # новая модель заказов
    HAS_ORDER_MODEL = True
except Exception:
    Order = None
    HAS_ORDER_MODEL = False


# -----------------------------
# Публичные ручки
# -----------------------------
@router.get("/", response_model=List[PaymentOut], tags=["Public"])
def list_payments(db: Session = Depends(get_db)):
    """Список всех платежей (публично)."""
    return get_all_payments(db)


@router.get("/history/payments", response_model=List[PaymentOut], tags=["Public"])
def public_payment_history(
    user_id: int = Query(..., ge=1),
    company_id: Optional[int] = Query(None, ge=1),
    db: Session = Depends(get_db),
):
    """История платежей по user/company (провайдер-агностично)."""
    q = db.query(Payment).filter(Payment.user_id == user_id)
    if company_id is not None:
        q = q.filter(Payment.company_id == company_id)
    items = q.order_by(Payment.created_at.desc()).all()

    return [
        PaymentOut(
            id=p.id,
            provider=p.provider,
            provider_invoice_id=p.provider_invoice_id,
            status=p.status,
            amount=float(p.amount or 0),
            currency=p.currency or "UAH",
            payment_url=p.payment_url,
            user_id=p.user_id,
            company_id=p.company_id,
            subscription_id=p.subscription_id,
            tariff=p.tariff,
            language=p.language,
            description=p.description,
            created_at=p.created_at,
            updated_at=getattr(p, "updated_at", None),
        )
        for p in items
    ]


@router.get("/history/orders", response_model=List[OrderOut], tags=["Public"])
def public_order_history(
    user_id: int = Query(..., ge=1),
    company_id: Optional[int] = Query(None, ge=1),
    db: Session = Depends(get_db),
):
    """
    История «заказов».
    1) Если есть таблица orders — читаем из неё.
    2) Иначе fallback: 1 платёж = 1 заказ (из payments).
    """
    try:
        if HAS_ORDER_MODEL and Order is not None:
            q = db.query(Order).filter(Order.user_id == user_id)
            if company_id is not None:
                q = q.filter(Order.company_id == company_id)
            rows = q.order_by(Order.sold_at.desc()).all()
            return [
                OrderOut(
                    id=r.id,
                    user_id=r.user_id,
                    company_id=r.company_id,
                    product_id=getattr(r, "product_id", None),
                    quantity=int(getattr(r, "quantity", 1) or 1),
                    total_price=float(getattr(r, "total_price", 0) or 0),
                    sold_at=r.sold_at,
                )
                for r in rows
            ]

        # fallback: 1 платёж = 1 заказ
        q = db.query(Payment).filter(Payment.user_id == user_id)
        if company_id is not None:
            q = q.filter(Payment.company_id == company_id)
        payments = q.order_by(Payment.created_at.desc()).all()
        return [
            OrderOut(
                id=p.id,  # используем id платежа как id заказа
                user_id=p.user_id,
                company_id=p.company_id,
                product_id=None,
                quantity=1,
                total_price=float(p.amount or 0),
                sold_at=p.created_at,
            )
            for p in payments
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"orders handler error: {e}")


# -----------------------------
# Debug (dev only)
# -----------------------------
@router.get("/__debug/ping", tags=["Debug"])
def debug_ping():
    return {"ok": True, "where": "public_history_router"}


@router.post("/__debug/orders-bootstrap", tags=["Debug"], status_code=status.HTTP_200_OK)
@router.get("/__debug/orders-bootstrap", tags=["Debug"], status_code=status.HTTP_200_OK)
def orders_bootstrap(db: Session = Depends(get_db)):
    """
    Idempotent: создаёт orders, делает backfill из payments, создаёт индексы.
    """
    sql = r"""
    CREATE TABLE IF NOT EXISTS orders (
        id               SERIAL PRIMARY KEY,
        payment_id       INT UNIQUE REFERENCES payments(id) ON DELETE CASCADE,
        user_id          INT NOT NULL REFERENCES users(id),
        company_id       INT,
        subscription_id  INT REFERENCES subscriptions(id),
        product_id       INT,
        category_id      INT REFERENCES categories(category_id),
        quantity         INT DEFAULT 1 NOT NULL,
        total_price      NUMERIC(10,2) NOT NULL,
        currency         VARCHAR(10) DEFAULT 'UAH',
        status           VARCHAR(20) DEFAULT 'completed',
        sold_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    CREATE INDEX IF NOT EXISTS idx_orders_user_id       ON orders(user_id);
    CREATE INDEX IF NOT EXISTS idx_orders_company_id    ON orders(company_id);
    CREATE INDEX IF NOT EXISTS idx_orders_subscription  ON orders(subscription_id);
    CREATE INDEX IF NOT EXISTS idx_orders_category_id   ON orders(category_id);
    CREATE INDEX IF NOT EXISTS idx_orders_status        ON orders(status);
    CREATE INDEX IF NOT EXISTS idx_orders_sold_at       ON orders(sold_at);

    INSERT INTO orders (
        payment_id, user_id, company_id, subscription_id, product_id, category_id, quantity,
        total_price, currency, status, sold_at, created_at
    )
    SELECT
        p.id,
        p.user_id,
        p.company_id,
        p.subscription_id,
        NULL::INT,
        NULL::INT,
        1,
        p.amount,
        COALESCE(p.currency, 'UAH'),
        CASE
          WHEN p.status IN ('paid','success','finished') THEN 'completed'
          WHEN p.status = 'pending' THEN 'pending'
          ELSE 'canceled'
        END,
        p.created_at,
        NOW()
    FROM payments p
    WHERE p.provider IN ('monobank','nowpayments')
    ON CONFLICT (payment_id) DO NOTHING;
    """
    db.execute(sqla_text(sql))
    db.commit()
    return {"ok": True}
