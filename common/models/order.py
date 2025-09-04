# common/models/order.py
from sqlalchemy import Column, Integer, Numeric, String, ForeignKey, TIMESTAMP, text, UniqueConstraint
from common.db.base import Base

class Order(Base):
    __tablename__ = "orders"
    __table_args__ = (
        UniqueConstraint("payment_id", name="uq_orders_payment_id"),
    )

    id = Column(Integer, primary_key=True, index=True)
    payment_id = Column(Integer, ForeignKey("payments.id", ondelete="CASCADE"), nullable=False, unique=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    company_id = Column(Integer, nullable=True)
    subscription_id = Column(Integer, ForeignKey("subscriptions.id"), nullable=True)

    product_id = Column(Integer, nullable=True)
    category_id = Column(Integer, ForeignKey("categories.category_id"), nullable=True)

    quantity = Column(Integer, nullable=False, server_default=text("1"))
    total_price = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(10), server_default="UAH")
    status = Column(String(20), server_default="completed")  # pending/completed/canceled

    sold_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
