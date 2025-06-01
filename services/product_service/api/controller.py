# services/product_service/api/controller.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from common.db.session import get_db
from common.models.products import Product
from common.models.categories import Category
from common.models.inventory import Inventory
from .schemas import ProductCreate, CategoryCreate, InventoryCreate
from common.custom_exceptions import ProductNotFoundException, ProductInventoryUpdateException
from sqlalchemy.exc import SQLAlchemyError

router = APIRouter()

# Создание нового продукта
@router.post("/products/", response_model=Product)
def create_product(product: ProductCreate, db: Session = Depends(get_db())):
    """
    Создание продукта.
    1. Проверка существования категории в базе данных.
    2. Создание продукта.
    3. Создание инвентаря для продукта.
    """
    try:
        # Проверка на существование категории
        category = db.query(Category).filter_by(name=product.category_name).first()
        if not category:
            raise HTTPException(status_code=404, detail=f"Category '{product.category_name}' not found")

        # Создание нового продукта
        db_product = Product(**product.dict())
        db.add(db_product)
        db.commit()
        db.refresh(db_product)

        # Создание инвентаря для нового продукта
        inventory_data = InventoryCreate(
            category_name=db_product.category_name,
            product_id=db_product.id,
            inventory_quantity=db_product.current_inventory,
        )
        try:
            create_inventory(inventory_data, db)
        except Exception as error:
            raise ProductInventoryUpdateException(f"Error creating inventory: {error}")

        return db_product

    except SQLAlchemyError as e:
        db.rollback()
        error_message = str(e)
        raise HTTPException(status_code=500, detail=f"Database error: {error_message}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

# Обновление атрибутов продукта
@router.put("/products/{product_id}", response_model=Product)
def update_product_attribute(product_id: int, updated_attributes: dict, db: Session = Depends(get_db)):
    """
    Обновление атрибутов продукта:
    - Обновление указанных атрибутов продукта в базе данных.
    - Если обновляется "current_inventory", то обновляется инвентарь.
    """
    try:
        db_product = db.query(Product).filter_by(id=product_id).first()

        if db_product:
            # Обновляем только указанные атрибуты
            for key, value in updated_attributes.items():
                if hasattr(db_product, key):
                    setattr(db_product, key, value)
            db.commit()
            db.refresh(db_product)

            # Если обновляется "current_inventory", обновляем инвентарь
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

            return {
                "success": True,
                "message": "Product attributes updated successfully",
                "product": db_product,
            }

        else:
            raise ProductNotFoundException(f"Product with ID {product_id} not found")

    except SQLAlchemyError as e:
        db.rollback()
        error_message = str(e)
        raise HTTPException(status_code=500, detail=f"Database error: {error_message}")
    except ProductNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ProductInventoryUpdateException as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

# Получение продукта по ID
@router.get("/products/{product_id}", response_model=Product)
def get_product_by_id(product_id: int, db: Session = Depends(get_db())):
    """
    Получение продукта по ID
    """
    try:
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise ProductNotFoundException("Product not found")
        return product
    except ProductNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))

# Получение всех продуктов
@router.get("/products/", response_model=list[Product])
def get_all_products(db: Session = Depends(get_db())):
    """
    Получение всех продуктов.
    """
    try:
        products = db.query(Product).all()
        return products
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

# Функция для создания инвентаря
def create_inventory(inventory: InventoryCreate, db: Session):
    db_inventory = Inventory(**inventory.dict())
    db.add(db_inventory)
    db.commit()
    db.refresh(db_inventory)
    return db_inventory

# Создание новой категории
@router.post("/categories/", response_model=Category)
def create_category(category: CategoryCreate, db: Session = Depends(get_db())):
    """
    Создание категории:
    - Проверка и валидация через Pydantic модель.
    - Создание категории в базе данных.
    """
    try:
        db_category = Category(**category.dict())
        db.add(db_category)
        db.commit()
        db.refresh(db_category)
        return db_category
    except SQLAlchemyError as e:
        db.rollback()
        error_message = str(e)
        raise HTTPException(status_code=500, detail=f"Database error: {error_message}")

# Получение категории по имени
@router.get("/categories/{category_name}", response_model=Category)
def get_category_by_name(category_name: str, db: Session = Depends(get_db())):
    """
    Получение категории по имени
    """
    category = db.query(Category).filter(Category.name == category_name).first()
    if category is None:
        raise HTTPException(status_code=404, detail=f"Category '{category_name}' not found")
    return category
