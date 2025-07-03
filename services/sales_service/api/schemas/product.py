# services/sales_service/api/schemas/product.py
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
    category_id: int
    current_inventory: int

# Создание продукта
class ProductCreate(BaseModel):
    name: str
    description: str
    price: float
    image: Optional[str]
    category_id: ProductCategory  # Тут можно оставить enum
    current_inventory: int

# Обновление продукта
class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    image: Optional[str] = None
    category_name: Optional[ProductCategory] = None
    current_inventory: Optional[int] = None

# Ответ на запрос продукта
# services/sales_service/api/schemas/product.py

class Product(BaseModel):
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
    category_id: int
    category_name: Optional[str]  # 👈 добавлено

    class Config:
        from_attributes = True


# Модель для инвентаря (если нужно)
class InventoryCreate(BaseModel):
    product_id: int
    category_id: int
    inventory_quantity: int
