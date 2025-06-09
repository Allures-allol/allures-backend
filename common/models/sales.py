# common/models/sales.py
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from common.db.base import Base
import datetime


class Sales(Base):
    __tablename__ = "sales"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    category_id = Column(Integer, ForeignKey("categories.category_id"))

    units_sold = Column(Integer, default=0, nullable=False)
    sold_at = Column(DateTime, default=datetime.datetime.utcnow)
    total_price = Column(Float, nullable=False)
    revenue = Column(Float, nullable=True)

    # product = relationship("Product", backref="sales")
    # user = relationship("User", back_populates="sales")
    category = relationship("Category", backref="sales")