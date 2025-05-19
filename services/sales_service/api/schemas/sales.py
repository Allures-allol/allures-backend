from pydantic import BaseModel, validator
from common.enums.product_enums import ProductCategory
from datetime import datetime
from typing import Optional

class SalesBase(BaseModel):
    product_id: int
    category_name: ProductCategory
    units_sold: int = 0

    @validator("category_name")
    def validate_category(cls, value):
        if value is not None:
            valid_values = [item for item in ProductCategory]
            if value not in valid_values:
                raise ValueError("Invalid category")
        return value

class SalesStats(BaseModel):
    product_id: Optional[int]
    category_name: Optional[str]
    last_sold_at: Optional[datetime]
    total_units_sold: int
    total_revenue: float

    class Config:
        from_attributes = True  # вместо orm_mode

class SalesCreate(SalesBase):
    pass


# ✅ Используется для возврата в response_model
class SalesOut(BaseModel):
    id: int
    product_id: int
    category_name: ProductCategory
    units_sold: int
    sold_at: datetime
    total_price: float
    revenue: Optional[float]

    class Config:
        from_attributes = True

class SalesRequestParams(BaseModel):
    product_id: Optional[int] = None
    category: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    group_by: Optional[str] = None
