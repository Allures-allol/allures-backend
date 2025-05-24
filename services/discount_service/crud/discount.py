# crud/discount.py
from services.discount_service.models.discount import Discount
from datetime import datetime


def create_discount(db, data):
    obj = Discount(**data.dict())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def get_valid_discounts(db):
    return db.query(Discount).filter(Discount.expires_at > datetime.utcnow()).all()