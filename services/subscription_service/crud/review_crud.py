#services/subscription_service/crud/review_crud.py
from sqlalchemy.orm import Session
from models.comment_models import Review
from schemas.comment_schemas import ReviewCreate

def create_comment(db: Session, review: ReviewCreate):
    db_review = Review(**review.dict())
    db.add(db_review)
    db.review()
    db.refresh(db_review)
    return db_review

def get_all_comments(db: Session):
    return db.query(Review).all()

def get_comments_by_category(db: Session, category: str):
    return db.query(Review).filter(Review.category == category).all()
