# services/product_service/api/schemas.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from common.enums.product_enums import ProductCategory

class ProductBase(BaseModel):
    name: str
    description: str
    price: float
    image: Optional[str] = None
    category_name: ProductCategory
    current_inventory: int

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    image: Optional[str] = None
    category_name: Optional[ProductCategory] = None
    current_inventory: Optional[int] = None

class Product(ProductBase):
    id: int
    created_at: datetime
    updated_at: datetime
    status: str

    class Config:
        from_attributes = True

class InventoryCreate(BaseModel):
    product_id: int
    category_name: str
    inventory_quantity: int
