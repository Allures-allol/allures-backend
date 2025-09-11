# services/review_service/api/routes_reviews.py
from typing import List, Optional
import unicodedata

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func

from common.db.session import engine, get_db
from common.models.subscriptions import Subscription
from services.review_service.models.review import Review as ReviewModel
from services.review_service.api.schemas import ReviewCreate, ReviewOut
from sqlalchemy.exc import ProgrammingError, OperationalError
from common.db.base import Base
from services.review_service.models.review import Review
from common.models.categories import Category
from common.models.products import Product as ProductModel

# контроллеры/CRUD
from services.review_service.api.controller import (
    create_review,
    get_reviews_by_product,
    get_reviews_by_status,
    update_review_status,
)

reviews_router = APIRouter()

_ALLOWED_LANGS = {"uk", "ru", "en"}
_SYNONYM_TO_CODE = {
    "базовий": "basic", "базовый": "basic", "basic": "basic",
    "просунутий": "advanced", "продвинутый": "advanced", "advanced": "advanced",
    "преміум": "premium", "премиум": "premium", "premium": "premium",
    "безкоштовна": "free", "бесплатная": "free", "free": "free",
}


def _norm_code_or_name(value: Optional[str]) -> Optional[str]:
    if not value:
        return None
    return "-".join(unicodedata.normalize("NFKC", value).strip().lower().split())


# ---------- Reviews CRUD ----------
@reviews_router.get("/", response_model=list[ReviewOut])
def get_all_reviews(db: Session = Depends(get_db)):
    try:
        return db.query(Review).all()
    except (ProgrammingError, OperationalError) as e:
        # Обычно тут "relation reviews does not exist"
        msg = str(e)
        if "does not exist" in msg or "UndefinedTable" in msg:
            # создаём таблицы и отдаём пусто
            Base.metadata.create_all(bind=engine)
            return []
        raise HTTPException(status_code=500, detail=f"DB error: {msg}")

@reviews_router.get("/product/{product_id}", response_model=List[ReviewOut], tags=["Reviews"])
def get_reviews_by_product_route(product_id: int, db: Session = Depends(get_db)):
    rows = get_reviews_by_product(db, product_id)
    if not rows:
        raise HTTPException(status_code=404, detail="Reviews not found")
    return rows

@reviews_router.post("/", response_model=ReviewOut, tags=["Reviews"])
def add_review(review: ReviewCreate, db: Session = Depends(get_db)):
    return create_review(db, review)

@reviews_router.get("/by-status", response_model=List[ReviewOut], tags=["Reviews"])
def get_reviews_by_status_route(status: str, db: Session = Depends(get_db)):
    return get_reviews_by_status(db, status)

@reviews_router.post("/moderate/{review_id}", response_model=ReviewOut, tags=["Reviews"])
def moderate_review(review_id: int, status: str, db: Session = Depends(get_db)):
    return update_review_status(db, review_id, status)

@reviews_router.put("/update-status/{review_id}", response_model=ReviewOut, tags=["Reviews"])
def update_review_status_put(review_id: int, status: str, db: Session = Depends(get_db)):
    allowed = {"PENDING", "APPROVED", "REJECTED"}
    if status not in allowed:
        raise HTTPException(status_code=400, detail=f"Invalid status. Choose {', '.join(allowed)}.")
    return update_review_status(db, review_id, status)

# удалить один отзыв
@reviews_router.delete("/reviews/{review_id}", status_code=204, tags=["Reviews"])
def delete_review(review_id: int, db: Session = Depends(get_db)):
    try:
        r = db.query(ReviewModel).filter(ReviewModel.id == review_id).first()
        if not r:
            raise HTTPException(status_code=404, detail="Review not found")
        db.delete(r)
        db.commit()
        return
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

# удалить все отзывы товара (опционально — одного user_id)
@reviews_router.delete("/product/{product_id}", tags=["Reviews"])
def delete_reviews_of_product(
    product_id: int,
    user_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
):
    try:
        q = db.query(ReviewModel).filter(ReviewModel.product_id == product_id)
        if user_id is not None:
            q = q.filter(ReviewModel.user_id == user_id)
        deleted = q.delete(synchronize_session=False)
        db.commit()
        return {"deleted": deleted}
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

# --- lookup подписки (удобно иметь прямо тут)
try:
    # pydantic v2
    from pydantic import BaseModel, ConfigDict
    class SubscriptionInfo(BaseModel):
        id: int
        code: str
        language: str
        name: str
        price: int
        duration_days: int
        product_limit: int
        promo_balance: int
        support_level: Optional[str] = None
        stats_access: bool
        description: Optional[str] = None
        model_config = ConfigDict(from_attributes=True)
except Exception:
    from pydantic import BaseModel
    class SubscriptionInfo(BaseModel):
        id: int
        code: str
        language: str
        name: str
        price: int
        duration_days: int
        product_limit: int
        promo_balance: int
        support_level: Optional[str] = None
        stats_access: bool
        description: Optional[str] = None
        class Config:
            orm_mode = True

@reviews_router.get("/subscriptions/lookup", response_model=SubscriptionInfo, tags=["Reviews"])
def lookup_subscription_via_review(
    subscription_id: Optional[int] = Query(None),
    subscription_name: Optional[str] = Query(None),
    lang: Optional[str] = Query(None, description="uk|ru|en"),
    db: Session = Depends(get_db),
):
    if lang and lang.strip().lower() not in {"uk", "ru", "en"}:
        raise HTTPException(status_code=400, detail="lang must be 'uk', 'ru' or 'en'")

    if subscription_id is not None:
        sub = db.query(Subscription).filter(Subscription.id == subscription_id).first()
        if not sub:
            raise HTTPException(status_code=404, detail="Подписка не найдена")
        if lang and (getattr(sub, "language", "") or "").lower() != lang.lower():
            raise HTTPException(status_code=404, detail="Подписка с таким языком не найдена")
        return sub

    if subscription_name:
        norm = subscription_name.strip().lower()
        code_or_name = _SYNONYM_TO_CODE.get(norm) or _norm_code_or_name(subscription_name)
        if code_or_name == "free":
            sub = db.query(Subscription).filter(Subscription.id == 1).first()
        else:
            sub = (
                db.query(Subscription)
                .filter(func.lower(func.btrim(Subscription.code)) == code_or_name)
                .first()
            ) or (
                db.query(Subscription)
                .filter(func.lower(func.btrim(Subscription.name)) == norm)
                .first()
            )
        if not sub:
            raise HTTPException(status_code=404, detail="Подписка не найдена")
        if lang and (getattr(sub, "language", "") or "").lower() != lang.lower():
            raise HTTPException(status_code=404, detail="Подписка с таким языком не найдена")
        return sub

    raise HTTPException(status_code=400, detail="Provide subscription_id or subscription_name")
