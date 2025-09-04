# services/payment_service/routers/monobank_routes.py
import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Header, Request, status
from sqlalchemy.orm import Session
from sqlalchemy import select

from common.db.session import get_db
from common.models.payment import Payment
from common.models.subscriptions import Subscription
from services.payment_service.schemas.monobank import MonoCreateInvoiceIn, MonoCreateInvoiceOut
from services.payment_service.crud.monobank import (
    monobank_create_invoice,
    create_mono_invoice,
    update_payment_status,
    get_all_mono_payments,
    get_payments_by_user,
    verify_monobank_signature,
    delete_payment,
    delete_payment_by_invoice_id,
)

router = APIRouter()


@router.post("/create", response_model=MonoCreateInvoiceOut, tags=["Monobank"])
async def monobank_create(invoice: MonoCreateInvoiceIn, db: Session = Depends(get_db)):
    order_id = invoice.order_id or str(uuid.uuid4())

    # проверим подписку
    sub_code = sub_name = None
    if invoice.subscription_id is not None:
        sub = db.execute(
            select(Subscription.code, Subscription.name).where(Subscription.id == invoice.subscription_id)
        ).first()
        if not sub:
            raise HTTPException(status_code=400, detail=f"Subscription {invoice.subscription_id} not found")
        sub_code, sub_name = sub

    # создаём инвойс в Monobank
    mono = await monobank_create_invoice(
        amount_uah=invoice.amount_uah,
        order_id=order_id,
        email=invoice.email,
    )

    payload = invoice.dict()
    payload["order_id"] = order_id
    p = create_mono_invoice(db=db, invoice=payload, page_url=mono["pageUrl"])

    return MonoCreateInvoiceOut(
        pageUrl=mono["pageUrl"],
        invoiceId=mono["invoiceId"],
        amount=invoice.amount_uah,
        currency=invoice.currency or "UAH",
        status=p.status,
        user_id=p.user_id,
        company_id=p.company_id,
        subscription_id=p.subscription_id,
        subscription_code=sub_code,
        subscription_name=sub_name,
        tariff=p.tariff,
        language=p.language,
        description=p.description,
    )


@router.post("/webhook", tags=["Monobank"])
async def monobank_webhook(
    request: Request,
    x_signature: Optional[str] = Header(None),
    db: Session = Depends(get_db),
):
    raw = await request.body()
    if not verify_monobank_signature(raw, x_signature):
        raise HTTPException(status_code=400, detail="Invalid signature")

    payload = await request.json()
    invoice_id = payload.get("invoiceId")
    status_val = str(payload.get("status", "")).lower()

    if not invoice_id or not status_val:
        raise HTTPException(status_code=400, detail="Missing invoiceId or status")

    p = update_payment_status(db, invoice_id, status_val)
    if not p:
        raise HTTPException(status_code=404, detail="Payment not found")

    return {"status": "ok", "invoiceId": invoice_id, "newStatus": status_val}


@router.get("/all", response_model=List[MonoCreateInvoiceOut], tags=["Monobank"])
def monobank_all(db: Session = Depends(get_db)):
    payments = get_all_mono_payments(db)

    result = []
    for p in payments:
        sub_code = sub_name = None
        if p.subscription_id:
            sub = db.execute(
                select(Subscription.code, Subscription.name).where(Subscription.id == p.subscription_id)
            ).first()
            if sub:
                sub_code, sub_name = sub
        result.append(
            MonoCreateInvoiceOut(
                pageUrl=p.payment_url or "",
                invoiceId=p.provider_invoice_id or "",
                amount=float(p.amount or 0),
                currency=p.currency or "UAH",
                status=p.status,
                user_id=p.user_id,
                company_id=p.company_id,
                subscription_id=p.subscription_id,
                subscription_code=sub_code,
                subscription_name=sub_name,
                tariff=p.tariff,
                language=p.language,
                description=p.description,
            )
        )
    return result


@router.get("/history/{user_id}", response_model=List[MonoCreateInvoiceOut], tags=["Monobank"])
def monobank_user_history(user_id: int, company_id: Optional[int] = None, db: Session = Depends(get_db)):
    payments = get_payments_by_user(db, user_id=user_id, company_id=company_id)

    result = []
    for p in payments:
        sub_code = sub_name = None
        if p.subscription_id:
            sub = db.execute(
                select(Subscription.code, Subscription.name).where(Subscription.id == p.subscription_id)
            ).first()
            if sub:
                sub_code, sub_name = sub
        result.append(
            MonoCreateInvoiceOut(
                pageUrl=p.payment_url or "",
                invoiceId=p.provider_invoice_id or "",
                amount=float(p.amount or 0),
                currency=p.currency or "UAH",
                status=p.status,
                user_id=p.user_id,
                company_id=p.company_id,
                subscription_id=p.subscription_id,
                subscription_code=sub_code,
                subscription_name=sub_name,
                tariff=p.tariff,
                language=p.language,
                description=p.description,
            )
        )
    return result


@router.delete("/{payment_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Monobank"])
def delete_payment_by_id(payment_id: int, db: Session = Depends(get_db)):
    ok = delete_payment(db, payment_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Payment not found")
    return


@router.delete("/by-invoice/{invoice_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Monobank"])
def delete_payment_invoice(invoice_id: str, db: Session = Depends(get_db)):
    ok = delete_payment_by_invoice_id(db, invoice_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Payment not found")
    return
