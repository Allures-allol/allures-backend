# common/models/order.py
from sqlalchemy import (
    Column, Integer, String, ForeignKey,
    Numeric, DateTime, TIMESTAMP, text, UniqueConstraint
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from common.db.base import Base


class Order(Base):
    __tablename__ = "orders"
    __table_args__ = (
        UniqueConstraint("payment_id", name="uq_orders_payment_id"),
    )

    id = Column(Integer, primary_key=True, index=True)

    # Привязка к платежу
    payment_id = Column(Integer, ForeignKey("payments.id", ondelete="CASCADE"), nullable=True, unique=True)

    # Базовые связи
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    company_id = Column(Integer, nullable=True)
    subscription_id = Column(Integer, ForeignKey("subscriptions.id"), nullable=True)

    # Если заказ напрямую по продукту (без корзины)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=True)
    category_id = Column(Integer, ForeignKey("categories.category_id"), nullable=True)

    # Если заказ создан из корзины
    cart_id = Column(Integer, ForeignKey("carts.id", ondelete="SET NULL"), nullable=True)

    # Атрибуты заказа
    quantity = Column(Integer, nullable=False, server_default=text("1"))
    total_amount = Column(Numeric(12, 2), nullable=False, default=0)   # общая сумма
    total_price = Column(Numeric(10, 2), nullable=True)               # для совместимости со старой схемой
    currency = Column(String(10), server_default="UAH")
    status = Column(
        String(20),
        nullable=False,
        server_default="CREATED"   # CREATED | PAID | COMPLETED | CANCELLED | SHIPPED
    )

    # Даты
    sold_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Реляции
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    qty = Column(Integer, nullable=False)
    price_snapshot = Column(Numeric(12, 2), nullable=False)

    order = relationship("Order", back_populates="items")
