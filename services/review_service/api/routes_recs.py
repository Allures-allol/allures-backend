# services/review_service/api/routes_recs.py
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from common.db.session import get_db
from common.models.products import Product as ProductModel
from services.review_service.models.review import Review
from services.review_service.models.recommendation import Recommendation as RecommendationModel
from services.review_service.api.schemas import (
    RecommendationCreate, RecommendationOut, QueryRequest, ProductOut
)
from services.review_service.logic.recommendation import (
    Product, recommend_products, save_recommendations_to_db
)

recs_router = APIRouter()

@recs_router.get("/recommendations/", response_model=List[RecommendationOut], tags=["Recommendations"])
def get_all_recommendations(db: Session = Depends(get_db)):
    return db.query(RecommendationModel).all()

@recs_router.get("/recommendations/user/{user_id}", response_model=List[RecommendationOut], tags=["Recommendations"])
def get_user_recommendations(user_id: int, db: Session = Depends(get_db)):
    return (
        db.query(RecommendationModel)
        .filter(RecommendationModel.user_id == user_id)
        .order_by(RecommendationModel.recommended_at.desc())
        .all()
    )

@recs_router.post("/recommendations/", response_model=List[ProductOut], tags=["Recommendations"])
def get_recommendations(data: QueryRequest, db: Session = Depends(get_db)):
    # TODO: привязать реального user_id из auth/JWT
    user_id = 999

    all_reviews = db.query(Review).all()
    product_map = {}
    for r in all_reviews:
        pid = r.product_id
        product_map.setdefault(pid, {
            "id": pid,
            "name": f"Product {pid}",
            "category": "unknown",
            "description": "",
            "reviews": []
        })
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
            pos_percent=round(p.pos_percent, 2),
        )
        for p, _ in recommendations
    ]

@recs_router.post("/recommendations/add", response_model=RecommendationOut, tags=["Recommendations"])
def add_recommendation(data: RecommendationCreate, db: Session = Depends(get_db)):
    obj = RecommendationModel(**data.dict())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

@recs_router.put("/recommendations/{id}", response_model=RecommendationOut, tags=["Recommendations"])
def update_recommendation(id: int, data: RecommendationCreate, db: Session = Depends(get_db)):
    obj = db.query(RecommendationModel).filter(RecommendationModel.id == id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Not found")
    for k, v in data.dict().items():
        setattr(obj, k, v)
    db.commit()
    db.refresh(obj)
    return obj

@recs_router.delete("/recommendations/{id}", status_code=204, tags=["Recommendations"])
def delete_recommendation(id: int, db: Session = Depends(get_db)):
    try:
        obj = db.query(RecommendationModel).filter(RecommendationModel.id == id).first()
        if not obj:
            raise HTTPException(status_code=404, detail="Recommendation not found")
        db.delete(obj)
        db.commit()
        return
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

@recs_router.get("/recommendations/joined/", response_model=List[dict], tags=["Recommendations"])
def get_recommendations_with_product_name(db: Session = Depends(get_db)):
    rows = (
        db.query(RecommendationModel, ProductModel.name.label("product_name"))
        .join(ProductModel, ProductModel.id == RecommendationModel.product_id)
        .all()
    )
    out = []
    for rec, product_name in rows:
        out.append({
            "id": rec.id,
            "user_id": rec.user_id,
            "product_id": rec.product_id,
            "product_name": product_name,
            "score": rec.score,
            "recommended_at": getattr(rec, "recommended_at", None),
        })
    return out
