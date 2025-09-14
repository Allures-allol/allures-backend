# services/product_service/api/routes_reviews.py
from typing import List,Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from pydantic import BaseModel


# ...
from common.db.session import get_db
from common.models.products import Product as ProductModel
from common.models.categories import Category as CategoryModel
from common.models.inventory import Inventory

from services.product_service.api.schemas import (
    ProductUpdate, ProductOut,
    InventoryCreate, CategoryCreate, Category as CategorySchema
)
from services.product_service.clients.review_client import (
    reviews_client, ReviewOut, RecommendationOut
)

router = APIRouter(strict_slashes=False)

# ---------- helpers ----------
def create_inventory(inventory: InventoryCreate, db: Session):
    db_inventory = Inventory(**inventory.dict())
    db.add(db_inventory)
    db.commit()
    db.refresh(db_inventory)
    return db_inventory

# ---------- PRODUCTS (упрощённые) ----------

@router.get("/", response_model=List[ProductOut], summary="List all products (no pagination)")
def list_products_simple(db: Session = Depends(get_db)):
    """Все товары по порядку (id ASC: 1,2,3,…)"""
    items = db.query(ProductModel).order_by(ProductModel.id.asc()).all()
    return [
        ProductOut(
            id=p.id, name=p.name, description=p.description,
            price=p.price, old_price=p.old_price, image=p.image,
            status=p.status, current_inventory=p.current_inventory,
            is_hit=p.is_hit, is_discount=p.is_discount, is_new=p.is_new,
            created_at=p.created_at, updated_at=p.updated_at,
            category_id=p.category_id, category_name=p.category_name,
            subcategory=p.subcategory, product_type=p.product_type,
            company_id=p.company_id,
        ) for p in items
    ]

@router.get("/company/{company_id}/products", response_model=List[ProductOut],
            summary="List company products (no pagination)")
def list_company_products(company_id: int, db: Session = Depends(get_db)):
    """Все товары конкретной компании (id ASC)."""
    items = (
        db.query(ProductModel)
          .filter(ProductModel.company_id == company_id)
          .order_by(ProductModel.id.asc())
          .all()
    )
    return [
        ProductOut(
            id=p.id, name=p.name, description=p.description,
            price=p.price, old_price=p.old_price, image=p.image,
            status=p.status, current_inventory=p.current_inventory,
            is_hit=p.is_hit, is_discount=p.is_discount, is_new=p.is_new,
            created_at=p.created_at, updated_at=p.updated_at,
            category_id=p.category_id, category_name=p.category_name,
            subcategory=p.subcategory, product_type=p.product_type,
            company_id=p.company_id,
        ) for p in items
    ]

@router.put("/{product_id}", response_model=ProductOut)
def update_product(
    product_id: int,
    update: ProductUpdate,
    db: Session = Depends(get_db),
    company_id: Optional[int] = Query(None, description="ID компании-владельца"),
):
    """Простой апдейт продукта. Если передан current_inventory — пишем снапшот в инвентарь."""
    try:
        db_product = db.query(ProductModel).filter_by(id=product_id).first()
        if not db_product:
            raise HTTPException(status_code=404, detail=f"Product with ID {product_id} not found")
        if company_id is not None and db_product.company_id != company_id:
            raise HTTPException(status_code=404, detail="Product not found")

        update_data = update.dict(exclude_unset=True)
        for k, v in update_data.items():
            setattr(db_product, k, v)

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

@router.delete("/{product_id}", status_code=204)
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    company_id: Optional[int] = Query(None, description="ID компании-владельца"),
):
    """Удалить продукт (опц. проверка владельца)."""
    prod = db.query(ProductModel).filter(ProductModel.id == product_id).first()
    if not prod:
        raise HTTPException(status_code=404, detail="Product not found")
    if company_id is not None and prod.company_id != company_id:
        raise HTTPException(status_code=404, detail="Product not found")
    try:
        db.delete(prod)
        db.commit()
        return Response(status_code=204)
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

# ---------- CATEGORIES ----------

@router.get("/categories", response_model=List[CategorySchema])
def list_categories(db: Session = Depends(get_db)):
    """Вернёт все категории (id ASC)."""
    return db.query(CategoryModel).order_by(CategoryModel.category_id.asc()).all()

@router.post("/categories/", response_model=CategorySchema)
def create_category(category: CategoryCreate, db: Session = Depends(get_db)):
    """Создать категорию (минимум полей)."""
    try:
        db_category = CategoryModel(**category.dict())
        db.add(db_category)
        db.commit()
        db.refresh(db_category)
        return db_category
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

class CategoryUpdate(BaseModel):
    category_name: Optional[str] = None

@router.patch("/categories/{category_id}", response_model=CategorySchema)
def patch_category(
    category_id: int,
    body: CategoryUpdate,
    db: Session = Depends(get_db),
):
    """Переименовать категорию + синхронизировать денормализованное имя в товарах."""
    cat = (
        db.query(CategoryModel)
          .filter(CategoryModel.category_id == category_id)
          .first()
    )
    if not cat:
        raise HTTPException(status_code=404, detail=f"Category with ID {category_id} not found")

    payload = body.dict(exclude_unset=True)
    if not payload:
        return cat

    if "category_name" in payload and payload["category_name"] is not None:
        new_name = payload["category_name"].strip()
        if not new_name:
            raise HTTPException(status_code=422, detail="category_name cannot be empty")

        dupe = (
            db.query(CategoryModel.category_id)
              .filter(
                  func.lower(func.btrim(CategoryModel.category_name)) == new_name.lower(),
                  CategoryModel.category_id != category_id
              )
              .first()
        )
        if dupe:
            raise HTTPException(status_code=409, detail="Category with this name already exists")

        cat.category_name = new_name
        db.query(ProductModel)\
          .filter(ProductModel.category_id == category_id)\
          .update({ProductModel.category_name: new_name}, synchronize_session=False)

    try:
        db.commit()
        db.refresh(cat)
        return cat
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get("/categories/{category_id}", response_model=CategorySchema)
def get_category_by_id(category_id: int, db: Session = Depends(get_db)):
    category = db.query(CategoryModel).filter(CategoryModel.category_id == category_id).first()
    if category is None:
        raise HTTPException(status_code=404, detail=f"Category with ID {category_id} not found")
    return category

@router.delete("/categories/{category_id}", status_code=204)
def delete_category(category_id: int, db: Session = Depends(get_db), force: bool = Query(False)):
    """Удалить категорию. Если есть товары и force=false — вернуть 409."""
    cat = db.query(CategoryModel).filter(CategoryModel.category_id == category_id).first()
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")

    has_products = db.query(ProductModel.id).filter(ProductModel.category_id == category_id).first()
    if has_products and not force:
        raise HTTPException(status_code=409, detail="Category has products; pass ?force=true to delete anyway")

    try:
        if force:
            db.query(ProductModel).filter(ProductModel.category_id == category_id).delete(synchronize_session=False)
        db.delete(cat)
        db.commit()
        return Response(status_code=204)
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get("/categories/{category_id}/products", response_model=List[ProductOut])
def list_category_products(
    category_id: int,
    db: Session = Depends(get_db),
    company_id: Optional[int] = Query(None, description="Фильтр по компании"),
):
    """Все товары по category_id (опц. фильтр по company_id), по убыванию id."""
    qset = db.query(ProductModel).filter(ProductModel.category_id == category_id)
    if company_id is not None:
        qset = qset.filter(ProductModel.company_id == company_id)

    products = qset.order_by(ProductModel.id.desc()).all()
    return [
        ProductOut(
            id=p.id, name=p.name, description=p.description,
            price=p.price, old_price=p.old_price, image=p.image,
            status=p.status, current_inventory=p.current_inventory,
            is_hit=p.is_hit, is_discount=p.is_discount, is_new=p.is_new,
            created_at=p.created_at, updated_at=p.updated_at,
            category_id=p.category_id, category_name=p.category_name,
            subcategory=p.subcategory, product_type=p.product_type,
            company_id=p.company_id,
        )
        for p in products
    ]

# ---------- PROXY -> REVIEW SERVICE ----------
# ВАЖНО: review_client должен указывать корректную базу.
# Если ваш review-сервис отдает эндпоинты на /review/… — база вида http://host:port/review.
# Если без /review (т.е. /product/... сразу от корня) — база вида http://host:port.

@router.get("/users/{user_id}/recommendations", response_model=List[RecommendationOut])
def get_user_recommendations(user_id: int):
    """Прокси: рекомендации для пользователя."""
    try:
        return reviews_client.get_user_recommendations(user_id)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Review service error: {e}")

@router.get("/{product_id}/reviews", response_model=List[ReviewOut])
def get_product_reviews(product_id: int):
    """Прокси: отзывы по продукту."""
    try:
        return reviews_client.get_reviews_by_product(product_id)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Review service error: {e}")

# ---------- DEBUG ----------
@router.get("/__debug/review_base")
def debug_review_base():
    """Текущая база, куда ходит review_client."""
    return {"review_base": reviews_client.get_base()}

@router.get("/__debug/review_probe")
def debug_review_probe():
    """Проверка нескольких эндпоинтов review-сервиса с каждой базой-кандидатом."""
    return reviews_client.probe()

# --- : DELETE proxies ---

@router.delete("/reviews/{review_id}", status_code=204, summary="Proxy: delete single review by id")
def proxy_delete_review(review_id: int):
    try:
        reviews_client.delete_review(review_id)
        return
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Review service error: {e}")

@router.delete("/{product_id}/reviews", summary="Proxy: delete all product reviews (optionally by user_id)")
def proxy_delete_reviews_of_product(product_id: int, user_id: Optional[int] = Query(None)):
    try:
        result = reviews_client.delete_reviews_of_product(product_id, user_id=user_id)
        return result  # {"deleted": N}
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Review service error: {e}")

@router.delete("/recommendations/{rec_id}", status_code=204, summary="Proxy: delete single recommendation")
def proxy_delete_recommendation(rec_id: int):
    try:
        reviews_client.delete_recommendation(rec_id)
        return
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Review service error: {e}")

@router.delete("/users/{user_id}/recommendations", summary="Proxy: delete all recommendations of a user")
def proxy_delete_recommendations_of_user(user_id: int):
    try:
        result = reviews_client.delete_recommendations_of_user(user_id)
        return result  # {"deleted": N}
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Review service error: {e}")
