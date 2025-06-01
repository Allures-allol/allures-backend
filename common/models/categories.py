# common/models/categories.py
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from common.db.base import Base

class Category(Base):
    __tablename__ = "categories"

    category_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False, unique=True, index=True)
    description = Column(String(255), nullable=True)

    # Lazy позволяет избежать загрузки связей сразу
    products = relationship("Product", back_populates="category", lazy="selectin")
    sales = relationship("Sales", back_populates="category", lazy="selectin")
