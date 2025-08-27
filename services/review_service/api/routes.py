# services/review_service/api/routes.py
from typing import Optional, List
import unicodedata
from fastapi import APIRouter, Query, HTTPException, Depends
from sqlalchemy import func, or_
from sqlalchemy.orm import Session
from common.db.session import get_db
from services.review_service.api import controller
from services.review_service.logic.recommendation import (
    Product, recommend_products, save_recommendations_to_db
)
from common.models.subscriptions import Subscription, UserSubscription
from services.review_service.models.review import Review
from services.review_service.models.recommendation import Recommendation
from services.review_service.api.schemas import (
    ReviewCreate, ReviewOut,
    RecommendationCreate, RecommendationOut,
    QueryRequest, ProductOut
)
from services.review_service.api.crud import (
    create_recommendation, update_recommendation,
    delete_recommendation, get_recommendations_filtered,
    get_reviews_by_subscription as crud_get_reviews_by_subscription
)

from common.models.products import Product as ProductModel
# Локальная схема для подписки, чтобы не тянуть импорт из subscription_service
try:
    # Pydantic v2
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
    # Pydantic v1 fallback
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


router = APIRouter()

# ---------- helpers (нормализация) ----------

_SYNONYM_TO_CODE = {
    "базовий": "basic", "базовый": "basic", "basic": "basic",
    "просунутий": "advanced", "продвинутый": "advanced", "advanced": "advanced",
    "преміум": "premium", "премиум": "premium", "premium": "premium",
    "безкоштовна": "free", "бесплатная": "free", "free": "free",
}
_ALLOWED_LANGS = {"uk", "ru", "en"}


def _norm(s: Optional[str]) -> Optional[str]:
    if s is None:
        return None
    return unicodedata.normalize("NFKC", s).strip().lower()


def _norm_code_or_name(value: Optional[str]) -> Optional[str]:
    if not value:
        return None
    return "-".join(value.strip().lower().split())


def _normalize_code_from_name(subscription_name: Optional[str]) -> Optional[str]:
    if not subscription_name:
        return None
    norm = subscription_name.strip().lower()
    return _SYNONYM_TO_CODE.get(norm) or _norm_code_or_name(subscription_name)

# === REVIEWS ===
@router.post("/", response_model=ReviewOut)
def add_review(review: ReviewCreate, db: Session = Depends(get_db)):
    return controller.create_review(db, review)

@router.get("/product/{product_id}", response_model=List[ReviewOut])
def get_reviews(product_id: int, db: Session = Depends(get_db)):
    # Совпадает с ProductService.review_client: /reviews/product/{product_id}
    return controller.get_reviews_by_product(db, product_id)

@router.get("/", response_model=List[ReviewOut])
def get_all_reviews(db: Session = Depends(get_db)):
    return db.query(Review).all()

@router.get("/user/{user_id}", response_model=List[ReviewOut])
def get_reviews_by_user(user_id: int, db: Session = Depends(get_db)):
    return db.query(Review).filter(Review.user_id == user_id).all()

@router.get("/by-subscription", response_model=List[ReviewOut])
def reviews_by_subscription(
    subscription_id: Optional[int] = Query(None, description="Точный ID подписки"),
    subscription_name: Optional[str] = Query(
        None,
        description="Free/Basic/Advanced/Premium или синонимы (укр/рус). Приоритет у ID."
    ),
    lang: Optional[str] = Query(None, description="ru|uk|en (опционально)"),
    db: Session = Depends(get_db),
):
    if subscription_id is None and not subscription_name:
        raise HTTPException(status_code=400, detail="Provide subscription_id or subscription_name")

    return crud_get_reviews_by_subscription(
        db=db,
        subscription_name=subscription_name,
        subscription_id=subscription_id,
        lang=lang,
    )


# --- lookup подписки прямо из review-сервиса (аналогично subscription_service/lookup) ---

@router.get("/subscriptions/lookup", response_model=SubscriptionInfo)
def lookup_subscription_via_review(
    subscription_id: Optional[int] = Query(None, description="ID подписки"),
    subscription_name: Optional[str] = Query(
        None,
        description=(
            "Безкоштовна/Бесплатная/Free, Базовий/Базовый/Basic, "
            "Просунутий/Продвинутый/Advanced, Преміум/Премиум/Premium"
        ),
    ),
    lang: Optional[str] = Query(None, description="uk|ru|en (опционально)"),
    db: Session = Depends(get_db),
):
    if lang and lang.strip().lower() not in _ALLOWED_LANGS:
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
            )
            if not sub:
                sub = (
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


# === RECOMMENDATIONS ===
@router.get("/recommendations/", response_model=List[RecommendationOut])
def get_all_recommendations(db: Session = Depends(get_db)):
    return db.query(Recommendation).all()

@router.get("/recommendations/user/{user_id}", response_model=List[RecommendationOut])
def get_user_recommendations(user_id: int, db: Session = Depends(get_db)):
    return (
        db.query(Recommendation)
        .filter(Recommendation.user_id == user_id)
        .order_by(Recommendation.recommended_at.desc())
        .all()
    )

@router.post("/recommendations/", response_model=List[ProductOut])
def get_recommendations(data: QueryRequest, db: Session = Depends(get_db)):
    user_id = 999  # временно

    all_reviews = db.query(Review).all()

    product_map = {}
    for r in all_reviews:
        pid = r.product_id
        if pid not in product_map:
            product_map[pid] = {
                "id": pid,
                "name": f"Product {pid}",
                "category": "unknown",
                "description": "",
                "reviews": []
            }
        # поддержка как r.text, так и r.comment
        text_val = getattr(r, "text", None) or getattr(r, "comment", "") or ""
        product_map[pid]["reviews"].append(text_val)

    product_objects = [Product(**p) for p in product_map.values()]
    recommendations = recommend_products(product_objects, data.query)
    save_recommendations_to_db(db, user_id, recommendations)

    return [
        ProductOut(
            id=p.id,
            name=p.name,
            sentiment_score=round(p.sentiment_score, 2),
            pos_percent=round(p.pos_percent, 2)
        )
        for p, _ in recommendations
    ]

@router.post("/recommendations/add", response_model=RecommendationOut)
def add_recommendation(data: RecommendationCreate, db: Session = Depends(get_db)):
    return create_recommendation(db, data)

@router.put("/recommendations/{id}", response_model=RecommendationOut)
def update_recommendation_route(id: int, data: RecommendationCreate, db: Session = Depends(get_db)):
    return update_recommendation(db, id, data)

@router.delete("/recommendations/{id}", status_code=204)
def delete_recommendation_route(id: int, db: Session = Depends(get_db)):
    delete_recommendation(db, id)
    return

@router.get("/recommendations/filtered/")
def get_filtered_recommendations(min_score: float = 0.5, db: Session = Depends(get_db)):
    # В некоторых схемах поля pos_score может не быть
    pos_col = getattr(Review, "pos_score", None)
    if pos_col is None:
        raise HTTPException(status_code=400, detail="Column pos_score not found in Review")
    return db.query(Review).filter(pos_col >= min_score).all()

@router.get("/recommendations/joined/", response_model=List[dict])
def get_recommendations_with_product_name(db: Session = Depends(get_db)):
    results = (
        db.query(
            Recommendation,
            ProductModel.name.label("product_name")
        )
        .join(ProductModel, ProductModel.id == Recommendation.product_id)
        .all()
    )
    # В orm-запросе вернётся Row с ключами по именам сущностей/полей
    out = []
    for r in results:
        rec = r[0] if isinstance(r, (tuple, list)) else getattr(r, "Recommendation", None) or r
        product_name = r[1] if isinstance(r, (tuple, list)) else getattr(r, "product_name", None)
        out.append({
            "id": rec.id,
            "user_id": rec.user_id,
            "product_id": rec.product_id,
            "product_name": product_name,
            "score": rec.score,
            "recommended_at": getattr(rec, "recommended_at", None)
        })
    return out
