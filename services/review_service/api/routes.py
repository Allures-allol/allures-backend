# services/review_service/api/routes.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from services.review_service.db.database import get_db
from services.review_service.models.review import Review
from services.review_service.models.recommendation import Recommendation

from services.review_service.api.schemas import (
    ReviewCreate, ReviewOut, RecommendationOut, QueryRequest, ProductOut
)
from services.review_service.api import controller
from services.review_service.logic.recommendation import (
    Product,
    recommend_products,
    save_recommendations_to_db
)

router = APIRouter()


@router.post("/reviews/", response_model=ReviewOut)
def add_review(review: ReviewCreate, db: Session = Depends(get_db)):
    return controller.create_review(db, review)


@router.get("/reviews/{product_id}", response_model=List[ReviewOut])
def get_reviews(product_id: int, db: Session = Depends(get_db)):
    return controller.get_reviews_by_product(db, product_id)


@router.get("/reviews/", response_model=List[ReviewOut])
def get_all_reviews(db: Session = Depends(get_db)):
    return db.query(Review).all()


@router.get("/recommendations/", response_model=List[RecommendationOut])
def get_all_recommendations(db: Session = Depends(get_db)):
    return db.query(Recommendation).all()


@router.post("/recommend/", response_model=List[ProductOut])
def get_recommendations(data: QueryRequest, db: Session = Depends(get_db)):
    user_id = 999  # временно, можно заменить при наличии токена

    all_reviews = db.query(Review).all()

    # Группировка отзывов по product_id
    product_map = {}
    for r in all_reviews:
        pid = r.product_id
        if pid not in product_map:
            product_map[pid] = {
                "id": pid,
                "name": f"Product {pid}",  # имя подставное, т.к. без ProductDb
                "category": "unknown",
                "description": "",
                "reviews": []
            }
        product_map[pid]["reviews"].append(r.text)

    # Формируем объекты Product для анализа
    product_objects = [Product(**p) for p in product_map.values()]
    recommendations = recommend_products(product_objects, data.query)

    # Сохраняем результат в БД
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

@router.get("/reviews/user/{user_id}", response_model=List[ReviewOut])
def get_reviews_by_user(user_id: int, db: Session = Depends(get_db)):
    return db.query(Review).filter(Review.user_id == user_id).all()
