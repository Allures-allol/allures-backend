# services/product_service/api/controller.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from common.db.session import get_db
from common.models.products import Product as ProductModel
from common.models.categories import Category as CategoryModel
from common.models.inventory import Inventory
from services.product_service.api.schemas import (
    ProductCreate, ProductUpdate, ProductOut, CategoryCreate,
    Category as CategorySchema, InventoryCreate
)
from common.custom_exceptions import (ProductNotFoundException, ProductInventoryUpdateException)

router = APIRouter()

def create_inventory(inventory: InventoryCreate, db: Session):
    db_inventory = Inventory(**inventory.dict())
    db.add(db_inventory)
    db.commit()
    db.refresh(db_inventory)
    return db_inventory

@router.post("/", response_model=ProductOut)
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    try:
        category = db.query(CategoryModel).filter_by(category_id=product.category_id).first()
        if not category:
            raise HTTPException(status_code=404, detail=f"Category '{product.category_id}' not found")

        db_product = ProductModel(**product.dict())
        db.add(db_product)
        db.commit()
        db.refresh(db_product)

        inventory_data = InventoryCreate(
            product_id=db_product.id,
            category_id=db_product.category_id,
            inventory_quantity=db_product.current_inventory,
        )
        create_inventory(inventory_data, db)

        return db_product

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


@router.put("/{product_id}", response_model=ProductOut)
def update_product_attribute(product_id: int, update: ProductUpdate, db: Session = Depends(get_db)):
    try:
        db_product = db.query(ProductModel).filter_by(id=product_id).first()
        if not db_product:
            raise HTTPException(status_code=404, detail=f"Product with ID {product_id} not found")

        update_data = update.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_product, key, value)

        db.commit()
        db.refresh(db_product)

        if "current_inventory" in update_data:
            inventory_data = InventoryCreate(
                product_id=product_id,
                category_id=db_product.category_id,
                inventory_quantity=update_data["current_inventory"],
            )
            create_inventory(inventory_data, db)

        return db_product

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


@router.get("/{product_id}", response_model=ProductOut)
def get_product_by_id(product_id: int, db: Session = Depends(get_db)):
    try:
        product = db.query(ProductModel).filter(ProductModel.id == product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        return product
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


@router.get("/", response_model=list[ProductOut])
def get_all_products(db: Session = Depends(get_db)):
    try:
        products = db.query(ProductModel).all()
        return products
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.post("/categories/", response_model=CategorySchema)
def create_category(category: CategoryCreate, db: Session = Depends(get_db)):
    try:
        db_category = CategoryModel(**category.dict())
        db.add(db_category)
        db.commit()
        db.refresh(db_category)
        return db_category
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.get("/categories/{category_id}", response_model=CategorySchema)
def get_category_by_id(category_id: int, db: Session = Depends(get_db)):
    category = db.query(CategoryModel).filter(CategoryModel.category_id == category_id).first()
    if category is None:
        raise HTTPException(status_code=404, detail=f"Category with ID {category_id} not found")
    return category
