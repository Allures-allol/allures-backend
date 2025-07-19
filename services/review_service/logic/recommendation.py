# services/review_service/logic/recommendation.py

from services.review_service.sentiment.analyzer import analyze_sentiment
from services.review_service.models.recommendation import Recommendation
from sqlalchemy.orm import Session
from typing import List, Dict, Tuple

class Product:
    def __init__(self, id: int, name: str, category: str, description: str, reviews: List[str]):
        self.id = id
        self.name = name
        self.category = category
        self.description = description
        self.reviews = reviews
        self.sentiment_score = 0
        self.pos_percent = 0

def process_user_query(query: str) -> List[str]:
    return query.lower().split()

def evaluate_reviews(reviews: List[str]) -> Dict[str, float]:
    total_pos = 0
    total_neg = 0
    for review in reviews:
        result = analyze_sentiment(review)
        total_pos += result['pos_score']
        total_neg += result['neg_score']
    total = len(reviews)
    avg_pos = total_pos / total if total else 0
    avg_neg = total_neg / total if total else 0
    final_score = (avg_pos - avg_neg + 100) / 2
    return {"avg_pos": avg_pos, "avg_neg": avg_neg, "final_score": final_score}

def keyword_match(product: Product, keywords: List[str]) -> int:
    matches = 0
    for kw in keywords:
        if kw in product.name.lower() or kw in product.description.lower():
            matches += 1
    return matches

def recommend_products(products: List[Product], user_query: str) -> List[Tuple[Product, float]]:
    keywords = process_user_query(user_query)
    scored = []
    for product in products:
        sentiment = evaluate_reviews(product.reviews)
        product.sentiment_score = sentiment["final_score"]
        product.pos_percent = sentiment["avg_pos"]
        score = keyword_match(product, keywords) * 50 + product.sentiment_score * 0.5
        scored.append((product, score))

    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:5]  # возвращаем top 5 пар (product, score)

def save_recommendations_to_db(db: Session, user_id: int, recommended: List[Tuple[Product, float]]):
    for product, score in recommended:
        rec = Recommendation(
            user_id=user_id,
            product_id=product.id,
            score=round(score, 2)
        )
        db.add(rec)
    db.commit()
