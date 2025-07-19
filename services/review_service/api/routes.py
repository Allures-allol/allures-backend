# services/review_service/api/routes.py
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from services.review_service.db.database import get_db
from services.review_service.api import controller
from services.review_service.logic.recommendation import (
    Product, recommend_products, save_recommendations_to_db
)
from services.review_service.models.review import Review
from services.review_service.models.recommendation import Recommendation
from services.review_service.api.schemas import (
    ReviewCreate, ReviewOut,
    RecommendationCreate, RecommendationOut,
    QueryRequest, ProductOut
)
from services.review_service.api.crud import (
    get_reviews_by_subscription_name,
    create_recommendation, update_recommendation,
    delete_recommendation, get_recommendations_filtered
)
from common.models.products import Product as ProductModel

router = APIRouter()

# === REVIEWS ===

@router.post("/reviews/", response_model=ReviewOut)
def add_review(review: ReviewCreate, db: Session = Depends(get_db)):
    return controller.create_review(db, review)


@router.get("/reviews/{product_id}", response_model=List[ReviewOut])
def get_reviews(product_id: int, db: Session = Depends(get_db)):
    return controller.get_reviews_by_product(db, product_id)


@router.get("/reviews/", response_model=List[ReviewOut])
def get_all_reviews(db: Session = Depends(get_db)):
    return db.query(Review).all()


@router.get("/reviews/user/{user_id}", response_model=List[ReviewOut])
def get_reviews_by_user(user_id: int, db: Session = Depends(get_db)):
    return db.query(Review).filter(Review.user_id == user_id).all()


@router.get("/by-subscription", response_model=List[ReviewOut])
def reviews_by_subscription(
    subscription_name: str = Query(..., description="Назва підписки (наприклад, Базовий, Продвинутий, Преміум)"),
    db: Session = Depends(get_db)
):
    return get_reviews_by_subscription_name(db, subscription_name)

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
        product_map[pid]["reviews"].append(r.text)

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
    return db.query(Review).filter(Review.pos_score >= min_score).all()


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

    return [
        {
            "id": r.Recommendation.id,
            "user_id": r.Recommendation.user_id,
            "product_id": r.Recommendation.product_id,
            "product_name": r.product_name,
            "score": r.Recommendation.score,
            "recommended_at": r.Recommendation.recommended_at
        }
        for r in results
    ]
