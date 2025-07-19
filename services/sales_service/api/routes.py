#sales_service/api/routes.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
import traceback

from common.db.session import get_db
from common.models.products import Product as ProductModel
from common.models.sales import Sales
from services.sales_service.api.schemas.sales import (
    SalesOut,
    SalesRequestParams,
    SalesStats,
    SalesCreate,
)
from services.sales_service.api.schemas.product import (
    Product as ProductOut,
    ProductCreate,
    ProductUpdate,
)
from common.custom_exceptions import (
    ProductNotFoundException,
    NoSalesDataFoundException,
)
from services.sales_service.api.controller import fetch_sales, create_product_sale_transaction

router = APIRouter()


# Создание продукта
@router.post("/products/", response_model=ProductOut, status_code=status.HTTP_201_CREATED)
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    db_product = ProductModel(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


# Получение всех продуктов (с category_name)
@router.get("/products/", response_model=List[ProductOut])
def get_filtered_products(
    db: Session = Depends(get_db),
    skip: int = Query(0, description="Сколько пропустить"),
    limit: int = Query(10, description="Сколько вернуть"),
    status: Optional[str] = Query(None, description="Фильтр по статусу ('active', 'inactive')"),
    min_price: Optional[float] = Query(None, description="Минимальная цена"),
    max_price: Optional[float] = Query(None, description="Максимальная цена"),
    is_new: Optional[bool] = Query(None, description="Фильтр новых продуктов"),
    search: Optional[str] = Query(None, description="Поиск по названию"),
):
    query = db.query(ProductModel).options(joinedload(ProductModel.category))

    if status:
        query = query.filter(ProductModel.status == status)

    if min_price is not None:
        query = query.filter(ProductModel.price >= min_price)

    if max_price is not None:
        query = query.filter(ProductModel.price <= max_price)

    if is_new is not None:
        query = query.filter(ProductModel.is_new == is_new)

    if search:
        query = query.filter(ProductModel.name.ilike(f"%{search}%"))

    products = query.offset(skip).limit(limit).all()

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
            category_name=p.category.name if p.category else None
        )
        for p in products
    ]


# Обновление продукта
@router.put("/products/{product_id}", response_model=ProductOut)
def update_product(product_id: int, updated: ProductUpdate, db: Session = Depends(get_db)):
    product = db.query(ProductModel).filter(ProductModel.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    for key, value in updated.dict(exclude_unset=True).items():
        setattr(product, key, value)

    db.commit()
    db.refresh(product)
    return product


# Получение всех продаж
@router.get("/sales/", response_model=List[SalesOut])
def get_all_sales(db: Session = Depends(get_db)):
    try:
        sales = db.query(Sales).all()
        if not sales:
            raise NoSalesDataFoundException("No sales found")
        return sales
    except Exception:
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail="Internal Server Error")


# Создание продажи с user_id
@router.post("/sales/", response_model=SalesOut, status_code=status.HTTP_201_CREATED)
def create_sale(sale: SalesCreate, db: Session = Depends(get_db)):
    try:
        return create_product_sale_transaction(sale.dict(), db)
    except Exception:
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail="Failed to create sale")

# Получение статистики продаж по параметрам
@router.post("/retrieve_sales", response_model=List[SalesStats])
def get_sales_for_product(params: SalesRequestParams, db: Session = Depends(get_db)):
    try:
        sales_data = fetch_sales(
            db,
            product_id=params.product_id,
            category_id=params.category_id,
            user_id=params.user_id,
            start_date=params.start_date,
            end_date=params.end_date,
            group_by=params.group_by,
        )
        if not sales_data:
            raise NoSalesDataFoundException("No sales data found for the specified criteria.")
        return sales_data

    except ProductNotFoundException as error:
        raise HTTPException(status_code=404, detail=str(error))
    except NoSalesDataFoundException as error:
        raise HTTPException(status_code=404, detail=str(error))
    except Exception:
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail="Internal Server Error")

# Получение всех продаж пользователя
@router.get("/sales/user/{user_id}", response_model=List[SalesOut])
def get_sales_by_user(user_id: int, db: Session = Depends(get_db)):
    try:
        sales = db.query(Sales).filter(Sales.user_id == user_id).all()
        if not sales:
            raise NoSalesDataFoundException(f"No sales found for user {user_id}")
        return sales
    except Exception:
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail="Internal Server Error")
