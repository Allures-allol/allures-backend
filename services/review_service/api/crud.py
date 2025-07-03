# 📁 services/review_service/crud/review_crud.py
from fastapi import HTTPException
from sqlalchemy.orm import Session
from typing import List

from services.review_service.models.review import Review
from services.review_service.models.recommendation import Recommendation
from services.review_service.api.schemas import ReviewCreate, RecommendationCreate
from common.models.user import User
from common.models.subscriptions import Subscription, UserSubscription


def create_review(db: Session, review: ReviewCreate) -> Review:
    new_review = Review(**review.dict())
    db.add(new_review)
    db.commit()
    db.refresh(new_review)
    return new_review


def get_all_reviews(db: Session):
    return db.query(Review).order_by(Review.created_at.desc()).all()


def get_reviews_by_sentiment(db: Session, sentiment: str):
    return db.query(Review).filter(Review.sentiment == sentiment).all()


def get_reviews_by_subscription_name(db: Session, subscription_name: str) -> List[Review]:
    subscription = db.query(Subscription).filter(Subscription.name == subscription_name).first()
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")

    return (
        db.query(Review)
        .join(UserSubscription, Review.user_id == UserSubscription.user_id)
        .join(Subscription, UserSubscription.subscription_id == Subscription.id)
        .filter(Subscription.name == subscription_name)
        .all()
    )


def create_recommendation(db: Session, data: RecommendationCreate) -> Recommendation:
    new_rec = Recommendation(**data.dict())
    db.add(new_rec)
    db.commit()
    db.refresh(new_rec)
    return new_rec


def update_recommendation(db: Session, rec_id: int, data: RecommendationCreate) -> Recommendation:
    rec = db.query(Recommendation).filter(Recommendation.id == rec_id).first()
    if not rec:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    rec.user_id = data.user_id
    rec.product_id = data.product_id
    rec.score = data.score
    db.commit()
    db.refresh(rec)
    return rec


def delete_recommendation(db: Session, rec_id: int):
    rec = db.query(Recommendation).filter(Recommendation.id == rec_id).first()
    if not rec:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    db.delete(rec)
    db.commit()


def get_recommendations_filtered(db: Session, min_score: float) -> List[Recommendation]:
    return (
        db.query(Recommendation)
        .filter(Recommendation.score >= min_score)
        .order_by(Recommendation.score.desc())
        .all()
    )
