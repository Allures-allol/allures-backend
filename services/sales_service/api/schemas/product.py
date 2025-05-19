# services/sales_service/api/schemas.py
from pydantic import BaseModel
from common.enums.product_enums import ProductCategory
from typing import Optional
from datetime import datetime

# Базовая модель
class ProductBase(BaseModel):
    name: str
    description: str
    price: float
    image: Optional[str] = None
    category_name: ProductCategory
    current_inventory: int

# Создание продукта
class ProductCreate(ProductBase):
    pass

# Обновление продукта
class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    image: Optional[str] = None
    category_name: Optional[ProductCategory] = None
    current_inventory: Optional[int] = None

# Ответ на запрос продукта
class Product(ProductBase):
    id: int
    created_at: datetime
    updated_at: datetime
    status: str

    class Config:
        from_attributes = True

# Модель для инвентаря (если нужно)
class InventoryCreate(BaseModel):
    product_id: int
    category_name: str
    inventory_quantity: int
