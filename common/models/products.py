# common/models/products.py
from sqlalchemy import Column, Integer, String, Float, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from common.db.base import Base
from sqlalchemy.sql import func
from common.models.categories import Category


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("categories.category_id"), nullable=False)
    name = Column(String(60), nullable=False)
    description = Column(String(255), nullable=False)
    price = Column(Float, nullable=False)
    image = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    status = Column(String(20), nullable=False)
    current_inventory = Column(Integer, nullable=False)

    category = relationship("Category", back_populates="products")