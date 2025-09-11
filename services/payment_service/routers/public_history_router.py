# services/payment_service/routers/public_history_router.py
from __future__ import annotations

from typing import List, Optional
from sqlalchemy.exc import IntegrityError
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text as sqla_text
from common.config.settings import settings
from common.db.session import get_db
from common.models.payment import Payment
from services.payment_service.crud.payment import get_all_payments
from services.payment_service.schemas.public import PaymentOut, OrderOut

# если Order не всегда есть:
try:
    from common.models.order import Order  # type: ignore
    HAS_ORDER_MODEL = True
except Exception:
    Order = None  # type: ignore
    HAS_ORDER_MODEL = False

router = APIRouter()

def _order_cols_available() -> List[str]:
    if not (HAS_ORDER_MODEL and Order is not None):
        return []
    # имена колонок, которые нам потенциально нужны
    wanted = [
        "id", "user_id", "company_id", "product_id", "category_id",
        "quantity", "total_price", "currency", "status",
        "sold_at", "created_at",
    ]
    # оставим только реально существующие в таблице
    existing = set(Order.__table__.columns.keys())
    return [c for c in wanted if c in existing]

def _row_to_out(row, colnames) -> dict:
    # row — это кортеж, если мы делали with_entities
    asdict = {name: val for name, val in zip(colnames, row)}
    return {
        "id": asdict.get("id"),
        "user_id": asdict.get("user_id"),
        "company_id": asdict.get("company_id"),
        "product_id": asdict.get("product_id"),
        "quantity": int(asdict.get("quantity") or 1),
        "total_price": float(asdict.get("total_price") or 0),
        "sold_at": asdict.get("sold_at") or asdict.get("created_at"),
    }
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
    История заказов.
    1) Если есть таблица orders — берём ТОЛЬКО реально существующие колонки (with_entities),
       чтобы не трогать отсутствующие (напр. cart_id).
    2) Иначе fallback: 1 платёж = 1 заказ (из payments).
    """
    try:
        # --- Путь через orders (безопасный выбор колонок) ---
        if HAS_ORDER_MODEL and Order is not None:
            colnames = _order_cols_available()
            if colnames:
                cols = [getattr(Order, c) for c in colnames]
                q = db.query(*cols).filter(getattr(Order, "user_id") == user_id)
                if company_id is not None and "company_id" in colnames:
                    q = q.filter(getattr(Order, "company_id") == company_id)

                # сортировка: sold_at -> created_at -> id
                if "sold_at" in colnames:
                    q = q.order_by(getattr(Order, "sold_at").desc())
                elif "created_at" in colnames:
                    q = q.order_by(getattr(Order, "created_at").desc())
                else:
                    q = q.order_by(getattr(Order, "id").desc())

                rows = q.all()
                return [OrderOut(**_row_to_out(r, colnames)) for r in rows]
            # если таблица есть, но из нужного набора не найдено ни одной колонки — уйдём на fallback

        # --- Fallback: 1 платёж = 1 заказ ---
        qp = db.query(Payment).filter(Payment.user_id == user_id)
        if company_id is not None and hasattr(Payment, "company_id"):
            qp = qp.filter(Payment.company_id == company_id)
        qp = qp.order_by(
            getattr(Payment, "created_at", Payment.id).desc()
        )
        payments = qp.all()
        return [
            OrderOut(
                id=p.id,
                user_id=p.user_id,
                company_id=getattr(p, "company_id", None),
                product_id=None,
                quantity=1,
                total_price=float(getattr(p, "amount", 0) or 0),
                sold_at=getattr(p, "created_at", None),
            )
            for p in payments
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"orders handler error: {e}")
@router.delete("/payment/delete/by-id/{payment_id}", summary="Удалить платёж по id")
def delete_payment_by_id(payment_id: int, db: Session = Depends(get_db)):
    obj = db.query(Payment).filter(Payment.id == payment_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Payment not found")
    try:
        db.delete(obj)
        db.commit()
    except IntegrityError as e:  # например, ссылка из orders без CASCADE
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Payment is referenced by other records (e.g., orders). Delete dependents first or add ON DELETE CASCADE."
        )
    return {"ok": True, "deleted_id": payment_id}

@router.delete("/payment/delete/by-invoice/{invoice_id}", summary="Удалить платёж по invoiceId")
def delete_payment_by_invoice(invoice_id: str, db: Session = Depends(get_db)):
    obj = (
        db.query(Payment)
          .filter(Payment.provider_invoice_id == invoice_id)
          .first()
    )
    if not obj:
        raise HTTPException(status_code=404, detail="Payment not found")
    try:
        db.delete(obj)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Payment is referenced by other records (e.g., orders). Delete dependents first or add ON DELETE CASCADE."
        )
    return {"ok": True, "deleted_invoice_id": invoice_id}
# -----------------------------
# Debug (dev only)
# -----------------------------
@router.get("/__debug/ping", tags=["Debug"])
def debug_ping():
    return {"ok": True, "where": "public_history_router"}

@router.get("/__debug/env", tags=["Debug"])
def dbg_env_probe():
    def mask(v: str | None) -> str:
        if not v: return ""
        if len(v) <= 8: return "***"
        return v[:4] + "..." + v[-4:]
    return {
        "DATABASE_URL_set": bool(settings.DATABASE_URL),
        "MAINDB_URL_set": bool(settings.MAINDB_URL),
        "POSTGRES_triplet_set": all([settings.POSTGRES_USER, settings.POSTGRES_PASSWORD, settings.POSTGRES_DB]),
        "effective_db_url_masked": mask(settings.effective_db_url),
    }

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
