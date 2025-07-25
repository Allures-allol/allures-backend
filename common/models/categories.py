# common/models/categories.py
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from common.db.base import Base

class Category(Base):
    __tablename__ = "categories"

    category_id = Column(Integer, primary_key=True, index=True)
    category_name = Column(String(50), unique=True, nullable=False)  # исправлено поле
    description = Column(String(255), nullable=True)

    subcategory = Column(String(100), nullable=True)
    product_type = Column(String(100), nullable=True)

    products = relationship("Product", back_populates="category", cascade="all, delete-orphan")
