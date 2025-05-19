# common/models/sales.py
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from common.db.base import Base
import datetime
from common.enums.product_enums import ProductCategory

class Sales(Base):
    __tablename__ = "sales"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    category_name = Column(String(50), ForeignKey("categories.name"), nullable=False)
    units_sold = Column(Integer, default=0, nullable=False)
    sold_at = Column(DateTime, default=datetime.datetime.utcnow)
    total_price = Column(Float, nullable=False)
    revenue = Column(Float, nullable=True)

    # 🔁 Эти импорты нужно переместить после класса, чтобы избежать циклической зависимости
    # product = relationship("Product", back_populates="sales")
    # category = relationship("Category", back_populates="sales")


# 👇 связываем после импортов:
from common.models.products import Product
from common.models.categories import Category

# Sales.product = relationship("Product", back_populates="sales")
# Sales.category = relationship("Category", back_populates="sales")