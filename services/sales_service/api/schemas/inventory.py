# api/schemas/inventory.py
from pydantic import BaseModel
from common.enums.product_enums import ProductCategory

class InventoryCreate(BaseModel):
    product_id: int
    category_id: ProductCategory  # Лучше использовать Enum для консистентности
    inventory_quantity: int

