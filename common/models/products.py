# common/models/products.py
from sqlalchemy import Column, Integer, String, Float, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey
from common.db.base import Base
from sqlalchemy.sql import func
from common.enums.product_enums import ProductCategory, ProductStatus

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    category_name = Column(String(50), ForeignKey("categories.name"), nullable=False)
    name = Column(String(60), nullable=False)
    description = Column(String(255), nullable=False)
    price = Column(Float, nullable=False)
    image = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    status = Column(Enum(ProductStatus), default=ProductStatus.active, nullable=False)
    current_inventory = Column(Integer, nullable=False)

    # category = relationship("Category", back_populates="products")
    # sales = relationship("common.models.sales.Sales", back_populates="product")

# 👇 связи прописываются после импорта нужных классов:
from common.models.sales import Sales
from common.models.categories import Category

#Product.category = relationship("Category", back_populates="products")
#Product.sales = relationship("Sales", back_populates="product")