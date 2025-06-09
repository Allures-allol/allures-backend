# services.payment_service/routers/payment.py
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel
from services.payment_service.schemas.payment import PaymentCreate, PaymentOut
from services.payment_service.crud.payment import create_payment, get_all_payments, create_nowpayment_invoice
from common.db.session import get_db
from fastapi.responses import JSONResponse
from common.config.settings import settings
from services.payment_service.common.config.settings_payment import settings_payment

router = APIRouter()

# Pydantic модель для ввода данных
class NowPaymentRequest(BaseModel):
    user_id: int
    amount: float
    currency: str = "USD"
    pay_currency: str = "BTC"
    order_description: str = "Test order"

@router.get("/", response_model=list[PaymentOut])
def read_all(db: Session = Depends(get_db)):
    return get_all_payments(db)

@router.post("/", response_model=PaymentOut)
def create(data: PaymentCreate, db: Session = Depends(get_db)):
    return create_payment(db, data)

@router.post("/nowpayment/")
async def create_nowpayment(data: NowPaymentRequest):
    # Собираем данные для запроса
    payload = {
        "price_amount": data.amount,
        "price_currency": data.currency.upper(),
        "pay_currency": data.pay_currency.lower(),
        "order_description": data.order_description,
        "ipn_callback_url": settings_payment.NGROK_WEBHOOK_URL
    }
    result = await create_nowpayment_invoice(payload)
    return result

@router.post("/webhook")
async def payment_webhook(request: Request, db: Session = Depends(get_db)):
    try:
        data = await request.json()
        print("🔔 Webhook received:", data)

        if data.get("payment_status") == "finished":
            # 💾 Сохраняем платеж в БД
            payment_data = PaymentCreate(
                user_id=1,  # Заменить на реальный user_id
                amount=float(data.get("pay_amount")),
                status="paid",
                payment_url=None
            )
            create_payment(db, payment_data)

        return {"status": "ok"}
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=400)
