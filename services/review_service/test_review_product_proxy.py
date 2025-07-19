# test_review_product_proxy.py

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from common.models.products import Product
from services.review_service.models.review import Review

# Загрузка переменных из .env
load_dotenv()

# Получение строки подключения
MAINDB_URL = os.getenv("MAINDB_URL")

# Создание подключения к БД
engine = create_engine(MAINDB_URL, echo=False, future=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def test_products_query():
    """
    ✅ Проверка получения продуктов и связанных с ними отзывов.
    """
    db = SessionLocal()
    try:
        products = db.query(Product).limit(5).all()
        assert products, "⚠️ Продукты не найдены"

        for p in products:
            category = p.category.name if p.category else "—"
            print(f"\n🛍 ID: {p.id} | Название: {p.name} | Категория: {category}")
            print(f"📝 Описание: {p.description}")

            reviews = db.query(Review).filter(Review.product_id == p.id).all()
            if reviews:
                print("💬 Отзывы:")
                for r in reviews:
                    print(f"  • [{r.sentiment.upper()}] {r.text}")
            else:
                print("🔕 Отзывов нет.")
    except Exception as e:
        assert False, f"❌ Ошибка запроса: {e}"
    finally:
        db.close()
