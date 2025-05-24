# services/payment_service/crud/payment.py
from services.payment_service.models.payment import Payment

def create_payment(db, data):
    obj = Payment(**data.dict())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

def get_all_payments(db):
    return db.query(Payment).all()