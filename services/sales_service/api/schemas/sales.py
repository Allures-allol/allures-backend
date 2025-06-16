# services/sales_service/api/schemas/sales.py
from pydantic import BaseModel, field_validator
from common.enums.product_enums import ProductCategory
from datetime import datetime
from typing import Optional

class SalesBase(BaseModel):
    product_id: int
    user_id: int
    category_id: int
    units_sold: int = 0

# Для создания новой продажи
class SalesCreate(SalesBase):
    pass

# Для возврата полной информации о продаже
class SalesOut(BaseModel):
    id: int
    product_id: int
    user_id: int
    category_id: int
    quantity: int
    sold_at: datetime
    total_price: float
    revenue: Optional[float] = None

    class Config:
        from_attributes = True

# Параметры запроса для фильтрации продаж
class SalesRequestParams(BaseModel):
    product_id: Optional[int] = None
    category_id: Optional[int] = None
    user_id: Optional[int] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    group_by: Optional[str] = None

# Результат статистики продаж
class SalesStats(BaseModel):
    product_id: Optional[int]
    category_id: Optional[int]
    user_id: Optional[int]
    last_sold_at: Optional[datetime]
    total_units_sold: int
    total_revenue: float

    class Config:
        from_attributes = True
