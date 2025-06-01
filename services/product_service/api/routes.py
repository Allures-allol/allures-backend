# services/product_service/api/routes.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from sqlalchemy.exc import SQLAlchemyError
from common.db.session import get_db
from common.models.products import Product as ProductModel
from common.models.categories import Category
from common.models.inventory import Inventory
from services.product_service.api.schemas import (
    ProductCreate,
    Product as ProductOut,
    InventoryCreate
)
from common.custom_exceptions import ProductNotFoundException, ProductInventoryUpdateException

router = APIRouter()

@router.post("/products/", response_model=ProductOut)
def create_product(product: ProductCreate, db: Session = Depends(get_db)):  # ✅ исправлено
    try:
        category = db.query(Category).filter_by(name=product.category_name).first()
        if not category:
            raise HTTPException(status_code=404, detail=f"Category '{product.category_name}' not found")

        db_product = ProductModel(**product.dict())
        db.add(db_product)
        db.commit()
        db.refresh(db_product)

        # Создание записи инвентаря
        inventory_data = InventoryCreate(
            product_id=db_product.id,
            category_name=db_product.category_name,
            inventory_quantity=db_product.current_inventory,
        )
        try:
            create_inventory(inventory_data, db)
        except Exception as error:
            raise ProductInventoryUpdateException(f"Error creating inventory: {error}")

        return db_product

    except SQLAlchemyError as e:
        db.rollback()
        return {"success": False, "message": f"Database error: {str(e)}"}
    except Exception as e:
        return {"success": False, "message": f"An error occurred: {str(e)}"}

@router.get("/products/", response_model=List[ProductOut])
def get_all_products(db: Session = Depends(get_db)):  # ✅ исправлено
    return db.query(ProductModel).all()

@router.get("/products/{product_id}", response_model=ProductOut)
def get_product_by_id(product_id: int, db: Session = Depends(get_db)):  # ✅ исправлено
    product = db.query(ProductModel).filter(ProductModel.id == product_id).first()
    if not product:
        raise ProductNotFoundException(f"Product with ID {product_id} not found")
    return product

@router.put("/products/{product_id}", response_model=ProductOut)
def update_product_attribute(product_id: int, updated_attributes: dict, db: Session = Depends(get_db)):  # ✅ исправлено
    try:
        db_product = db.query(ProductModel).filter_by(id=product_id).first()
        if not db_product:
            raise ProductNotFoundException(f"Product with ID {product_id} not found")

        for key, value in updated_attributes.items():
            if hasattr(db_product, key):
                setattr(db_product, key, value)
        db.commit()
        db.refresh(db_product)

        if "current_inventory" in updated_attributes:
            inventory_data = InventoryCreate(
                product_id=product_id,
                category_name=db_product.category_name,
                inventory_quantity=updated_attributes["current_inventory"],
            )
            try:
                create_inventory(inventory_data, db)
            except Exception as error:
                raise ProductInventoryUpdateException(f"Error updating inventory: {error}")

        return db_product

    except SQLAlchemyError as e:
        db.rollback()
        return {"success": False, "message": f"Database error: {str(e)}"}
    except Exception as e:
        return {"success": False, "message": f"An error occurred: {str(e)}"}

def create_inventory(inventory: InventoryCreate, db: Session):
    db_inventory = Inventory(**inventory.dict())
    db.add(db_inventory)
    db.commit()
    db.refresh(db_inventory)
    return db_inventory
