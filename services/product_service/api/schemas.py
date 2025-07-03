# services/product_service/api/schemas.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# === Категория товара ===
class CategoryCreate(BaseModel):
    name: str
    description: Optional[str] = None

class Category(BaseModel):
    category_id: int
    name: str
    description: Optional[str] = None

    class Config:
        from_attributes = True


# === Продукт ===
class ProductBase(BaseModel):
    name: str
    description: str
    price: float
    old_price: Optional[float] = None
    image: Optional[str] = None
    status: str
    current_inventory: int
    category_id: int
    is_hit: Optional[bool] = False
    is_discount: Optional[bool] = False
    is_new: Optional[bool] = False


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    old_price: Optional[float] = None
    image: Optional[str] = None
    status: Optional[str] = None
    current_inventory: Optional[int] = None
    category_id: Optional[int] = None
    is_hit: Optional[bool] = None
    is_discount: Optional[bool] = None
    is_new: Optional[bool] = None


class ProductOut(BaseModel):
    id: int
    name: str
    description: str
    price: float
    old_price: Optional[float]
    image: Optional[str]
    status: str
    current_inventory: int
    is_hit: Optional[bool]
    is_discount: Optional[bool]
    is_new: Optional[bool]
    created_at: datetime
    updated_at: datetime
    category_name: str

    class Config:
        from_attributes = True


class InventoryCreate(BaseModel):
    product_id: int
    category_id: int
    inventory_quantity: int
