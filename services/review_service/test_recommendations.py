# test_recommendations.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from services.review_service.models.product_proxy import ProductDb
from services.review_service.models.review import Review
from services.review_service.sentiment.analyzer import analyze_sentiment
from services.review_service.logic.recommendation import process_user_query, keyword_match
from datetime import datetime

# 1️⃣ Настройки подключения к БД
ALLURES_DB_URL = "mssql+pyodbc://localhost,1433/AlluresDb?driver=ODBC%20Driver%2017%20for%20SQL%20Server&;Trusted_Connection=yes"
REVIEW_DB_URL = "mssql+pyodbc://localhost,1433/ReviewDb?driver=ODBC%20Driver%2017%20for%20SQL%20Server&;Trusted_Connection=yes"

ProductSession = sessionmaker(bind=create_engine(ALLURES_DB_URL))
ReviewSession = sessionmaker(bind=create_engine(REVIEW_DB_URL))

# 2️⃣ Временная модель продукта
class Product:
    def __init__(self, id, name, category, description, reviews):
        self.id = id
        self.name = name
        self.category = category
        self.description = description
        self.reviews = reviews
        self.sentiment_score = 0
        self.pos_percent = 0

# 3️⃣ Подсчёт отзывов
def evaluate_reviews(reviews):
    total_pos, total_neg = 0, 0
    for text in reviews:
        result = analyze_sentiment(text)
        total_pos += result["pos_score"]
        total_neg += result["neg_score"]
    total = len(reviews)
    avg_pos = total_pos / total if total else 0
    avg_neg = total_neg / total if total else 0
    score = (avg_pos - avg_neg + 100) / 2
    return avg_pos, avg_neg, score

# 4️⃣ Основная логика рекомендаций
def recommend(query):
    product_db = ProductSession()
    review_db = ReviewSession()

    try:
        keywords = process_user_query(query)
        products = product_db.query(ProductDb).all()
        reviews = review_db.query(Review).all()

        product_reviews = {}
        for review in reviews:
            product_reviews.setdefault(review.product_id, []).append(review.text)

        enriched = []
        for p in products:
            if p.id not in product_reviews:
                continue
            revs = product_reviews[p.id]
            avg_pos, avg_neg, score = evaluate_reviews(revs)
            relevance = keyword_match(Product(p.id, p.name, p.category_name, p.description, revs), keywords)
            final_score = relevance * 50 + score * 0.5
            enriched.append((p, round(avg_pos, 2), round(score, 2), round(final_score, 2)))

        enriched.sort(key=lambda x: x[3], reverse=True)
        top = enriched[:5]

        print(f"\n🔎 Топ-5 рекомендаций по запросу: \"{query}\"")
        for p, pos, senti, total in top:
            print(f"✅ {p.name} ({p.category_name}) | pos: {pos}% | score: {senti} | общий: {total}")
    finally:
        product_db.close()
        review_db.close()

# 5️⃣ Запуск
if __name__ == "__main__":
    recommend("удобный рюкзак")
    recommend("зимняя куртка")
    recommend("тактические ботинки")
