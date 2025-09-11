# common/models/cart.py
from sqlalchemy import Column, Integer, String, ForeignKey, Numeric, DateTime, func
from sqlalchemy.orm import relationship
from common.db.base import Base

class Cart(Base):
    __tablename__ = "carts"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    status = Column(String, nullable=False, default="ACTIVE")  # ACTIVE | CONVERTED | ABANDONED
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    items = relationship("CartItem", back_populates="cart", cascade="all, delete-orphan")

class CartItem(Base):
    __tablename__ = "cart_items"
    id = Column(Integer, primary_key=True)
    cart_id = Column(Integer, ForeignKey("carts.id", ondelete="CASCADE"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    qty = Column(Integer, nullable=False)
    price_snapshot = Column(Numeric(12, 2), nullable=False)

    cart = relationship("Cart", back_populates="items")
