# common/models/products.py
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from common.db.base import Base

class Product(Base):
    __tablename__ = "products"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(String(255), nullable=False)
    price = Column(Float, nullable=False)
    old_price = Column(Float, nullable=True)
    image = Column(String(255), nullable=True)
    status = Column(String(20), nullable=False)
    current_inventory = Column(Integer, nullable=False)

    is_hit = Column(Boolean, default=False)
    is_discount = Column(Boolean, default=False)
    is_new = Column(Boolean, default=False)

    category_id = Column(Integer, ForeignKey("categories.category_id"), nullable=False)
    category_name = Column(String(50), nullable=False)  # если хочешь дублировать имя

    subcategory = Column(String(100), nullable=True)
    product_type = Column(String(100), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # category = relationship("Category", back_populates="products")
    #
    # sales = relationship("Sales", back_populates="product", cascade="all, delete-orphan")
    # reviews = relationship("Review", back_populates="product", cascade="all, delete-orphan")
