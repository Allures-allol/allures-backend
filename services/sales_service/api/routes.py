#sales_service/api/routes.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
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

import traceback

router = APIRouter()

# ✅ Создание продукта
@router.post("/products/", response_model=ProductOut, status_code=status.HTTP_201_CREATED)
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    db_product = ProductModel(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

# ✅ Получение всех продуктов
@router.get("/products/", response_model=List[ProductOut])
def get_all_products(db: Session = Depends(get_db)):
    return db.query(ProductModel).all()

# ✅ Обновление продукта
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

# ✅ Получение всех продаж
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

# ✅ Создание продажи с user_id
@router.post("/sales/", response_model=SalesOut, status_code=status.HTTP_201_CREATED)
def create_sale(sale: SalesCreate, db: Session = Depends(get_db)):
    try:
        return create_product_sale_transaction(sale.dict(), db)
    except Exception:
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail="Failed to create sale")

# ✅ Получение статистики продаж по параметрам, включая user_id
@router.post("/retrieve_sales", summary="Get sales for product", response_model=List[SalesStats])
def get_sales_for_product(params: SalesRequestParams, db: Session = Depends(get_db)):
    try:
        sales_data = fetch_sales(
            db,
            product_id=params.product_id,
            category_id=params.category_id,
            user_id=params.user_id,  # 🔹 Добавлена поддержка user_id
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

@router.get("/sales/user/{user_id}", response_model=List[SalesOut])
def get_sales_by_user(user_id: int, db: Session = Depends(get_db)):
    return db.query(Sales).filter(Sales.user_id == user_id).all()
