# services/product_service/api/routes.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import and_, or_
from typing import List, Optional

from common.db.session import get_db
from common.models.products import Product as ProductModel
from common.models.categories import Category as CategoryModel
from common.models.inventory import Inventory

from services.product_service.api.schemas import (
    ProductCreate, ProductUpdate, ProductOut, ProductsPage, PageMeta,
    InventoryCreate, CategoryCreate, Category as CategorySchema
)

# импорт HTTP‑клиента для отзывов
from services.product_service.api.review_client import (
    reviews_client, ReviewOut, RecommendationOut
)

router = APIRouter()

def create_inventory(inventory: InventoryCreate, db: Session):
    db_inventory = Inventory(**inventory.dict())
    db.add(db_inventory)
    db.commit()


    db.refresh(db_inventory)
    return db_inventory

# === Продукты ===
@router.get("/{product_id}", response_model=ProductOut)
def get_product_by_id(product_id: int, db: Session = Depends(get_db)):
    product = db.query(ProductModel).filter(ProductModel.id == product_id).first()
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

# === Категории ===

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

# === Прокси к Review Service (HTTP), без ORM‑связей ===

@router.get("/{product_id}/reviews", response_model=List[ReviewOut])
def get_product_reviews(product_id: int):
    try:
        return reviews_client.get_reviews_by_product(product_id)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Review service error: {e}")

@router.get("/users/{user_id}/recommendations", response_model=List[RecommendationOut])
def get_user_recommendations(user_id: int):
    try:
        return reviews_client.get_user_recommendations(user_id)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Review service error: {e}")

# ---------- Хелпер ----------
def apply_product_filters(q, *,
    search: Optional[str],
    category_id: Optional[int],
    is_new: Optional[bool],
    is_discount: Optional[bool],
    is_hit: Optional[bool],
    price_min: Optional[float],
    price_max: Optional[float],
    status: Optional[str],
):
    if search:
        like = f"%{search.strip()}%"
        q = q.filter(or_(ProductModel.name.ilike(like),
                         ProductModel.description.ilike(like)))
    if category_id is not None:
        q = q.filter(ProductModel.category_id == category_id)
    if is_new is not None:
        q = q.filter(ProductModel.is_new == is_new)
    if is_discount is not None:
        q = q.filter(ProductModel.is_discount == is_discount)
    if is_hit is not None:
        q = q.filter(ProductModel.is_hit == is_hit)
    if price_min is not None:
        q = q.filter(ProductModel.price >= price_min)
    if price_max is not None:
        q = q.filter(ProductModel.price <= price_max)
    if status:
        q = q.filter(ProductModel.status == status)
    return q

# ---------- ПАГИНАЦИЯ/СПИСОК ----------
@router.get("/", response_model=ProductsPage)
def list_products(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    category_id: Optional[int] = None,
    is_new: Optional[bool] = None,
    is_discount: Optional[bool] = None,
    is_hit: Optional[bool] = None,
    price_min: Optional[float] = None,
    price_max: Optional[float] = None,
    status: Optional[str] = None,
    sort: Optional[str] = Query(None, description="name|price|created_at|updated_at (добавь -desc для убывания)"),
):
    q = db.query(ProductModel)
    q = apply_product_filters(
        q,
        search=search,
        category_id=category_id,
        is_new=is_new,
        is_discount=is_discount,
        is_hit=is_hit,
        price_min=price_min,
        price_max=price_max,
        status=status,
    )

    # сортировка
    sort_map = {
        "name": ProductModel.name,
        "price": ProductModel.price,
        "created_at": ProductModel.created_at,
        "updated_at": ProductModel.updated_at,
    }
    if sort:
        desc = sort.endswith("-desc")
        key = sort[:-5] if desc else sort
        col = sort_map.get(key)
        if col is not None:
            q = q.order_by(col.desc() if desc else col.asc())
    else:
        q = q.order_by(ProductModel.id.asc())

    total = q.count()
    items = q.offset((page - 1) * per_page).limit(per_page).all()

    return ProductsPage(
        items=[
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
            ) for p in items
        ],
        meta=PageMeta(page=page, per_page=per_page, total=total),
    )