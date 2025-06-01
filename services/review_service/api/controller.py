# services/review_service/api/controller.py
from sqlalchemy.orm import Session
from services.review_service.models.review import Review
from services.review_service.models.recommendation import Recommendation
from services.review_service.api.schemas import ReviewCreate
from services.review_service.sentiment.analyzer import analyze_sentiment


def create_review(db: Session, review_data: ReviewCreate):
    result = analyze_sentiment(review_data.text)
    new_review = Review(
        product_id=review_data.product_id,
        user_id=review_data.user_id,
        text=review_data.text,
        sentiment=result["sentiment"],
        pos_score=result["pos_score"],
        neg_score=result["neg_score"]
    )
    db.add(new_review)
    db.commit()
    db.refresh(new_review)
    return new_review


def get_reviews_by_product(db: Session, product_id: int):
    return db.query(Review).filter(Review.product_id == product_id).all()


def save_recommendation(db: Session, user_id: int, product_id: int, score: float):
    record = Recommendation(user_id=user_id, product_id=product_id, score=score)
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def get_all_reviews(db: Session):
    return db.query(Review).all()


def get_all_recommendations(db: Session):
    return db.query(Recommendation).all()
