# test_recommendations.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from common.models.products import Product
from services.review_service.models.review import Review
from services.review_service.sentiment.analyzer import analyze_sentiment
from services.review_service.logic.recommendation import process_user_query, keyword_match
from services.review_service.common.config.settings_review import settings_review

# Подключение к базе данных
DATABASE_URL = settings_review.MAINDB_URL
engine = create_engine(DATABASE_URL, future=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Временная модель продукта
class ProductData:
    def __init__(self, id, name, category_name, description, reviews):
        self.id = id
        self.name = name
        self.category_name = category_name
        self.description = description
        self.reviews = reviews
        self.sentiment_score = 0
        self.pos_percent = 0

# Оценка отзывов
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

# Логика рекомендаций
def recommend(query):
    db = SessionLocal()
    try:
        keywords = process_user_query(query)
        products = db.query(Product).all()
        reviews = db.query(Review).all()

        product_reviews = {}
        for review in reviews:
            product_reviews.setdefault(review.product_id, []).append(review.text)

        enriched = []
        for p in products:
            if p.id not in product_reviews or not p.category:
                continue
            revs = product_reviews[p.id]
            avg_pos, avg_neg, score = evaluate_reviews(revs)
            relevance = keyword_match(
                ProductData(p.id, p.name, p.category.name if p.category else "—", p.description, revs),
                keywords
            )
            final_score = relevance * 50 + score * 0.5
            enriched.append((p, round(avg_pos, 2), round(score, 2), round(final_score, 2)))

        enriched.sort(key=lambda x: x[3], reverse=True)
        top = enriched[:5]

        print(f"\n Топ-5 рекомендаций по запросу: \"{query}\"")
        for p, pos, senti, total in top:
            print(f" {p.name} ({p.category.name if p.category else '—'}) | pos: {pos}% | score: {senti} | общий: {total}")
    finally:
        db.close()

# Тест для pytest
def test_recommend_runs_without_errors():
    try:
        recommend("рюкзак")
        recommend("куртка")
        recommend("ботинки")
    except Exception as e:
        assert False, f"Ошибка при выполнении recommend(): {e}"

# Локальный запуск
if __name__ == "__main__":
    recommend("удобный рюкзак")
    recommend("зимняя куртка")
    recommend("тактические ботинки")
