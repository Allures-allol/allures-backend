# common/db/models/inventory.py
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from common.db.base import Base

class Inventory(Base):
    __tablename__ = "inventory"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    category_name = Column(String, nullable=False)
    inventory_quantity = Column(Integer, nullable=False)

    # Связь с Product
    product = relationship("Product", back_populates="inventory", lazy="selectin")
