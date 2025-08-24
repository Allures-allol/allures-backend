# services/product_service/api/routes.py
from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy import func
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from typing import List, Optional

from common.db.session import get_db
from common.models.products import Product as ProductModel
from common.models.categories import Category as CategoryModel
from common.models.inventory import Inventory

from services.product_service.api.schemas import (
    ProductCreate, ProductUpdate, ProductOut, ProductsPage, PageMeta,
    InventoryCreate, CategoryCreate, Category as CategorySchema, ProductCreateMinimal
)
from services.product_service.clients.review_client import (
    reviews_client, ReviewOut, RecommendationOut
)

router = APIRouter()

# ---------- helpers ----------
def create_inventory(inventory: InventoryCreate, db: Session):
    db_inventory = Inventory(**inventory.dict())
    db.add(db_inventory)
    db.commit()
    db.refresh(db_inventory)
    return db_inventory

# ---------- LIST: PRODUCTS (общий список с пагинацией) ----------
@router.get("/", response_model=ProductsPage)
def list_products_simple(
    db: Session = Depends(get_db),
    offset: int = Query(0, ge=0, description="Смещение от начала"),
    limit: int = Query(20, ge=1, le=100, description="Сколько записей вернуть"),
    q: Optional[str] = Query(None, description="Поиск по name/description"),
    sort: Optional[str] = Query("-id", description="id|price|created_at|updated_at; '-' для DESC"),
):
    qset = db.query(ProductModel)
    if q:
        like = f"%{q.strip()}%"
        qset = qset.filter(
            (ProductModel.name.ilike(like)) |
            (ProductModel.description.ilike(like))
        )

    sort_map = {
        "id": ProductModel.id,
        "price": ProductModel.price,
        "created_at": ProductModel.created_at,
        "updated_at": ProductModel.updated_at,
    }
    desc = sort.startswith("-") if sort else True
    key = (sort[1:] if desc else sort) or "id"
    col = sort_map.get(key, ProductModel.id)
    qset = qset.order_by(col.desc() if desc else col.asc())

    total = qset.count()
    items = qset.offset(offset).limit(limit).all()

    return ProductsPage(
        items=[ProductOut(
            id=p.id, name=p.name, description=p.description,
            price=p.price, old_price=p.old_price, image=p.image,
            status=p.status, current_inventory=p.current_inventory,
            is_hit=p.is_hit, is_discount=p.is_discount, is_new=p.is_new,
            created_at=p.created_at, updated_at=p.updated_at,
            category_id=p.category_id, category_name=p.category_name,
            subcategory=p.subcategory, product_type=p.product_type
        ) for p in items],
        meta=PageMeta(page=(offset // limit + 1), per_page=limit, total=total),
    )

# ---------- CATEGORIES ----------
@router.get("/categories", response_model=List[CategorySchema])
def list_categories(db: Session = Depends(get_db)):
    """Вернёт все категории."""
    return db.query(CategoryModel).order_by(CategoryModel.category_id.asc()).all()

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

@router.delete("/categories/{category_id}", status_code=204)
def delete_category(category_id: int, db: Session = Depends(get_db), force: bool = Query(False)):
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

# ---------- PRODUCTS OF CATEGORY (простой список без пагинации) ----------
@router.get("/categories/{category_id}/products", response_model=List[ProductOut])
def list_category_products(category_id: int, db: Session = Depends(get_db)):
    """Все товары по category_id. Пустой список, если ничего не найдено."""
    return (
        db.query(ProductModel)
          .filter(ProductModel.category_id == category_id)
          .order_by(ProductModel.id.desc())
          .all()
    )

# ---------- PROXY -> REVIEW SERVICE ----------
@router.get("/users/{user_id}/recommendations", response_model=List[RecommendationOut])
def get_user_recommendations(user_id: int):
    try:
        return reviews_client.get_user_recommendations(user_id)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Review service error: {e}")

@router.get("/{product_id}/reviews", response_model=List[ReviewOut])
def get_product_reviews(product_id: int):
    try:
        return reviews_client.get_reviews_by_product(product_id)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Review service error: {e}")

# ---------- PRODUCTS CRUD ----------
@router.get("/all", response_model=List[ProductOut])
def get_all_products_raw(db: Session = Depends(get_db)):
    """Полный список без пагинации — для быстрой проверки/админки."""
    return db.query(ProductModel).order_by(ProductModel.id.desc()).all()

@router.get("/{product_id}", response_model=ProductOut)
def get_product_by_id(product_id: int, db: Session = Depends(get_db)):
    product = db.query(ProductModel).filter(ProductModel.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail=f"Product with ID {product_id} not found")
    return product

@router.post("/products/", response_model=ProductOut, status_code=201)
def create_product_minimal(body: ProductCreateMinimal, db: Session = Depends(get_db)):
    # требуем хотя бы один способ указания категории
    if body.category_id is None and not body.category_name:
        raise HTTPException(status_code=400, detail="Укажите category_id или category_name")

    # нормализуем категорию
    category_id = body.category_id
    category_name = body.category_name

    if category_id is not None:
        cat = db.query(CategoryModel).filter(CategoryModel.category_id == category_id).first()
        if not cat:
            raise HTTPException(status_code=404, detail=f"Категория id={category_id} не найдена")
        category_name = cat.category_name
    else:
        norm = body.category_name.strip().lower()
        cat = (db.query(CategoryModel)
               .filter(func.lower(func.btrim(CategoryModel.category_name)) == norm)
               .order_by(CategoryModel.category_id.asc())
               .first())
        if not cat:
            raise HTTPException(status_code=404, detail=f"Категория '{body.category_name}' не найдена")
        category_id = cat.category_id
        category_name = cat.category_name

    # пред-проверка дубля (как в уникальном индексе lower(btrim(name)), category_id)
    name_norm = body.name.strip().lower()
    duplicate = (db.query(ProductModel.id)
                 .filter(func.lower(func.btrim(ProductModel.name)) == name_norm,
                         ProductModel.category_id == category_id)
                 .first())
    if duplicate:
        raise HTTPException(409, f"Товар '{body.name.strip()}' уже существует в категории id={category_id}")

    # создание
    db_product = ProductModel(
        name=body.name.strip(),
        description=(body.description or "").strip(),
        price=body.price,
        old_price=None,
        image=(body.image or None),
        status="active",
        current_inventory=0,
        is_hit=False,
        is_discount=False,
        is_new=False,
        category_id=category_id,
        category_name=category_name,
        subcategory=(body.subcategory or None),
        product_type=body.product_type or "physical",
    )

    try:
        db.add(db_product)
        db.commit()
        db.refresh(db_product)
        return db_product
    except IntegrityError as e:
        db.rollback()
        # разбор pgcode/constraint
        pgcode = getattr(getattr(e, "orig", None), "pgcode", None)
        cname = getattr(getattr(getattr(e, "orig", None), "diag", None), "constraint_name", None)

        if pgcode == "23505":  # unique_violation
            if cname == "products_pkey":
                raise HTTPException(409, "Конфликт PK (products_pkey): вероятно, рассинхрон sequence. Нужен setval().")
            raise HTTPException(409, f"Дубликат (unique constraint): {cname or 'unknown'}")
        if pgcode == "23503":  # foreign_key_violation
            raise HTTPException(409, "Некорректная категория (FK violation)")
        if pgcode == "23502":  # not_null_violation
            raise HTTPException(422, "Нарушение NOT NULL")

        raise HTTPException(400, f"Integrity error: {str(e)}")
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"DB error: {str(e)}")

@router.put("/{product_id}", response_model=ProductOut)
def update_product(product_id: int, update: ProductUpdate, db: Session = Depends(get_db)):
    try:
        db_product = db.query(ProductModel).filter_by(id=product_id).first()
        if not db_product:
            raise HTTPException(status_code=404, detail=f"Product with ID {product_id} not found")

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
def delete_product(product_id: int, db: Session = Depends(get_db)):
    prod = db.query(ProductModel).filter(ProductModel.id == product_id).first()
    if not prod:
        raise HTTPException(status_code=404, detail="Product not found")
    try:
        db.delete(prod)
        db.commit()
        return Response(status_code=204)
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
