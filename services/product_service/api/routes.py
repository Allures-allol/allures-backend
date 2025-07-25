# services/product_service/api/routes.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Optional

from common.db.session import get_db
from common.models.products import Product as ProductModel
from common.models.categories import Category as CategoryModel
from common.models.inventory import Inventory
from services.product_service.api.schemas import (
    ProductCreate, ProductUpdate, ProductOut,
    InventoryCreate, CategoryCreate, Category as CategorySchema
)

router = APIRouter()

# Вспомогательная функция

def create_inventory(inventory: InventoryCreate, db: Session):
    db_inventory = Inventory(**inventory.dict())
    db.add(db_inventory)
    db.commit()
    db.refresh(db_inventory)
    return db_inventory

# Получение всех продуктов с категорией
@router.get("/", response_model=List[ProductOut])
def get_all_products(db: Session = Depends(get_db)):
    products = db.query(ProductModel).options(joinedload(ProductModel.category)).all()
    return [
        ProductOut(
            id=p.id,
            name=p.name,
            description=p.description,
            price=p.price,
            old_price=p.old_price,
            image=p.image,
            status=p.status,
            current_inventory=p.current_inventory,
            is_hit=p.is_hit,
            is_discount=p.is_discount,
            is_new=p.is_new,
            created_at=p.created_at,
            updated_at=p.updated_at,
            category_id=p.category_id,
            category_name=p.category_name,
            subcategory=p.subcategory,
            product_type=p.product_type,
        ) for p in products
    ]

# Получение продукта по ID
@router.get("/{product_id}", response_model=ProductOut)
def get_product_by_id(product_id: int, db: Session = Depends(get_db)):
    product = db.query(ProductModel).options(joinedload(ProductModel.category)).filter(ProductModel.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail=f"Product with ID {product_id} not found")

    return ProductOut(
        id=product.id,
        name=product.name,
        description=product.description,
        price=product.price,
        old_price=product.old_price,
        image=product.image,
        status=product.status,
        current_inventory=product.current_inventory,
        is_hit=product.is_hit,
        is_discount=product.is_discount,
        is_new=product.is_new,
        created_at=product.created_at,
        updated_at=product.updated_at,
        category_id=product.category_id,
        category_name=product.category_name,
        subcategory=product.subcategory,
        product_type=product.product_type,
    )

# Обновление продукта
@router.put("/{product_id}", response_model=ProductOut)
def update_product(product_id: int, update: ProductUpdate, db: Session = Depends(get_db)):
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

        return ProductOut(
            id=db_product.id,
            name=db_product.name,
            description=db_product.description,
            price=db_product.price,
            old_price=db_product.old_price,
            image=db_product.image,
            status=db_product.status,
            current_inventory=db_product.current_inventory,
            is_hit=db_product.is_hit,
            is_discount=db_product.is_discount,
            is_new=db_product.is_new,
            created_at=db_product.created_at,
            updated_at=db_product.updated_at,
            category_id=db_product.category_id,
            category_name=db_product.category_name,
            subcategory=db_product.subcategory,
            product_type=db_product.product_type,
        )

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

# Создание новой категории
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

# Получение категории по ID
@router.get("/categories/{category_id}", response_model=CategorySchema)
def get_category_by_id(category_id: int, db: Session = Depends(get_db)):
    category = db.query(CategoryModel).filter(CategoryModel.category_id == category_id).first()
    if category is None:
        raise HTTPException(status_code=404, detail=f"Category with ID {category_id} not found")
    return category
