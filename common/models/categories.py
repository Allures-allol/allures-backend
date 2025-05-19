# common/models/categories.py
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from common.db.base import Base
from common.enums.product_enums import ProductCategory
from sqlalchemy import Enum


class Category(Base):
    __tablename__ = "categories"

    category_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False, unique=True, index=True)
    description = Column(String(255), nullable=True)

    # Названия должны совпадать с relationship в связанных моделях
    # products = relationship("Product", back_populates="category")
    # sales = relationship("Sales", back_populates="category")

# 👇 связи тоже ниже
from common.models.products import Product
from common.models.sales import Sales

# Category.products = relationship("Product", back_populates="category")
# Category.sales = relationship("Sales", back_populates="category")