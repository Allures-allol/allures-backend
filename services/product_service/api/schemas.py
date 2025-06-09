from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# from common.enums.product_enums import ProductCategory  # не используется, можно удалить

class ProductBase(BaseModel):
    name: str
    description: str
    price: float
    image: Optional[str] = None
    category_id: int
    current_inventory: int
    status: str

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: Optional[str]
    description: Optional[str]
    price: Optional[float]
    image: Optional[str]
    category_id: Optional[int]
    current_inventory: Optional[int]
    status: Optional[str]

# 👉 используем его как response_model
class Product(ProductBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class CategoryCreate(BaseModel):
    name: str
    description: str

class InventoryCreate(BaseModel):
    product_id: int
    category_id: int
    inventory_quantity: int
