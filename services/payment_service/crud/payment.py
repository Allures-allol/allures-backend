# services/payment_service/crud/payment.py
from services.payment_service.models.payment import Payment
import httpx
from common.config.settings import settings

def create_payment(db, data):
    obj = Payment(**data.dict())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

def get_all_payments(db):
    return db.query(Payment).all()


async def create_nowpayment_invoice(data):
    api_key = settings.NOWPAYMENTS_API_KEY
    url = "https://api.nowpayments.io/v1/invoice"
    headers = {"x-api-key": api_key}

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=data, headers=headers)
        response.raise_for_status()  # Для отлова ошибок от NOWPayments
        return response.json()
