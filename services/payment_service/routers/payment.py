# services.payment_service/routers/payment.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from services.payment_service.schemas.payment import PaymentCreate, PaymentOut
from services.payment_service.crud.payment import create_payment, get_all_payments
from common.db.session import get_db

router = APIRouter()

@router.post("/", response_model=PaymentOut)
def create(data: PaymentCreate, db: Session = Depends(get_db)):
    return create_payment(db, data)

@router.get("/", response_model=list[PaymentOut])
def read_all(db: Session = Depends(get_db)):
    return get_all_payments(db)