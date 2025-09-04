# services/payment_service/crud/orders.py
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select
from common.models.order import Order

def get_orders_by_user(db: Session, user_id: int, company_id: Optional[int] = None) -> List[Order]:
    q = db.query(Order).filter(Order.user_id == user_id)
    if company_id is not None:
        q = q.filter(Order.company_id == company_id)
    return q.order_by(Order.sold_at.desc()).all()

def get_order_by_payment_id(db: Session, payment_id: int) -> Optional[Order]:
    return db.query(Order).filter(Order.payment_id == payment_id).first()
