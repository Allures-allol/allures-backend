from sqlalchemy.orm import Session
from services.review_service.models.review import Review
from services.review_service.api.schemas import ReviewCreate

def create_review(db: Session, review: ReviewCreate) -> Review:
    new_review = Review(**review.dict())
    db.add(new_review)
    db.commit()
    db.refresh(new_review)
    return new_review

def get_all_reviews(db: Session):
    return db.query(Review).order_by(Review.created_at.desc()).all()

