from pydantic import BaseModel
from typing import Optional

class CategoryCreate(BaseModel):
    name: str
    description: Optional[str] = None


class Category(BaseModel):
    category_id: int
    name: str
    description: Optional[str] = None

    class Config:
        from_attributes = True  # Используем FastAPI 0.100+ совместимость

