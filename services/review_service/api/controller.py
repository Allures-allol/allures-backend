# services/review_service/api/controller.py
from sqlalchemy.orm import Session
from services.review_service.models.review import Review
from services.review_service.models.recommendation import Recommendation
from services.review_service.api.schemas import ReviewCreate
from services.review_service.sentiment.analyzer import analyze_sentiment
from fastapi import HTTPException

def create_review(db: Session, review_data: ReviewCreate):
    # Анализируем текст отзыва для определения настроения
    result = analyze_sentiment(review_data.text)

    # Создаем новый отзыв с изначально статусом "pending"
    new_review = Review(
        product_id=review_data.product_id,
        user_id=review_data.user_id,
        text=review_data.text,
        sentiment=result["sentiment"],
        pos_score=result["pos_score"],
        neg_score=result["neg_score"],
        status="PENDING"  # Строка вместо Enum
    )

    try:
        db.add(new_review)
        db.commit()
        db.refresh(new_review)
        return new_review
    except Exception as e:
        db.rollback()  # В случае ошибки откатываем изменения
        raise HTTPException(status_code=500, detail=f"Error saving review: {str(e)}")


def get_reviews_by_product(db: Session, product_id: int):
    return db.query(Review).filter(Review.product_id == product_id).all()


def save_recommendation(db: Session, user_id: int, product_id: int, score: float):
    # Сохранение рекомендации для продукта
    record = Recommendation(user_id=user_id, product_id=product_id, score=score)
    try:
        db.add(record)
        db.commit()
        db.refresh(record)
        return record
    except Exception as e:
        db.rollback()  # В случае ошибки откатываем изменения
        raise HTTPException(status_code=500, detail=f"Error saving recommendation: {str(e)}")


def get_all_reviews(db: Session):
    return db.query(Review).all()


def get_all_recommendations(db: Session):
    return db.query(Recommendation).all()


# Новый метод для получения отзывов по статусу (например, для модерации)
def get_reviews_by_status(db: Session, status: str):
    return db.query(Review).filter(Review.status == status).all()


# Метод для обновления статуса отзыва
def update_review_status(db: Session, review_id: int, status: str):
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    review.status = status  # Строковое значение для статуса
    db.commit()
    db.refresh(review)
    return review
