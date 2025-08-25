# services/product_service/api/schemas.py
from pydantic import BaseModel, Field, HttpUrl, model_validator
from typing import  List, Optional
from datetime import datetime

# === Категория товара ===
class CategoryCreate(BaseModel):
    category_name: str
    description: Optional[str] = None
    subcategory: Optional[str] = None
    product_type: Optional[str] = None

class Category(BaseModel):
    category_id: int
    category_name: str
    description: Optional[str] = None
    subcategory: Optional[str] = None
    product_type: Optional[str] = None

    class Config:
        from_attributes = True

class ProductCreateMinimal(BaseModel):
    company_id: int
    name: str
    price: float
    description: str = ""
    image: Optional[str] = None
    category_id: Optional[int] = None
    category_name: Optional[str] = None
    subcategory: Optional[str] = None
    product_type: Optional[str] = "physical"

# === Продукт ===
class ProductCreate(BaseModel):
    name: str
    description: str
    price: float
    current_inventory: int = 0
    status: str = "active"

    category_id: int
    category_name: str

    # опционально
    old_price: Optional[float] = None
    image: Optional[str] = None
    subcategory: Optional[str] = None
    product_type: Optional[str] = "physical"

class ProductBase(BaseModel):
    name: str
    description: str
    price: float
    old_price: Optional[float] = None
    image: Optional[str] = None
    status: str
    current_inventory: int
    category_id: int
    category_name: str
    subcategory: Optional[str] = None
    product_type: Optional[str] = None
    is_hit: Optional[bool] = False
    is_discount: Optional[bool] = False
    is_new: Optional[bool] = False

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    old_price: Optional[float] = None
    image: Optional[str] = None
    status: Optional[str] = None
    current_inventory: Optional[int] = None
    category_id: Optional[int] = None
    category_name: Optional[str] = None
    subcategory: Optional[str] = None
    product_type: Optional[str] = None
    is_hit: Optional[bool] = None
    is_discount: Optional[bool] = None
    is_new: Optional[bool] = None

class ProductOut(BaseModel):
    id: int
    company_id: int
    name: str
    description: str
    price: float
    status: str
    current_inventory: int
    category_id: int
    category_name: str

    old_price: Optional[float] = None
    image: Optional[str] = None
    subcategory: Optional[str] = None
    product_type: Optional[str] = None

    is_hit: bool
    is_discount: bool
    is_new: bool

    created_at: datetime
    updated_at: datetime

    company_id: int

    class Config:
        from_attributes = True  # для .from_orm() / возврата из ORM


class InventoryCreate(BaseModel):
    product_id: int
    category_id: int
    inventory_quantity: int

class PageMeta(BaseModel):
    page: int
    per_page: int
    total: int

class ProductsPage(BaseModel):
    items: List[ProductOut]
    meta: PageMeta

class CategoryList(BaseModel):
    items: List[Category]
    meta: PageMeta