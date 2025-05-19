# services/review_service/models/product_proxy.py

from sqlalchemy import Column, Integer, String, Float, DateTime
from services.review_service.db.database import Base

class ProductDb(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    category_name = Column(String(50), nullable=False)
    name = Column(String(60), nullable=False)
    description = Column(String(255), nullable=False)
    price = Column(Float, nullable=True)
    image = Column(String(255), nullable=True)
    created_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)
    status = Column(String(20), nullable=True)
    current_inventory = Column(Integer, nullable=True)


