from pydantic import BaseModel, field_validator
from common.enums.product_enums import ProductCategory
from datetime import datetime
from typing import Optional

class SalesBase(BaseModel):
    product_id: int
    user_id: int
    category_id: int
    units_sold: int = 0

    @field_validator("category_id", mode="before")
    @classmethod
    def validate_category(cls, value):
        valid_values = [item.value for item in ProductCategory]
        if value not in valid_values:
            raise ValueError("Invalid category")
        return value

# Для создания новой продажи
class SalesCreate(SalesBase):
    pass

# Для возврата полной информации о продаже
class SalesOut(BaseModel):
    id: int
    product_id: int
    category_id: int
    user_id: Optional[int]  # ✅ добавлено
    units_sold: int
    sold_at: datetime
    total_price: float
    revenue: Optional[float]

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
