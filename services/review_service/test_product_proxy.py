# services/review_service/test_product_proxy.py

# test_product_proxy.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from services.review_service.models.product_proxy import ProductDb
from services.review_service.models.review import Review

# 🔧 Подключение к AlluresDb (продукты)
ALLURES_DB_URL = "mssql+pyodbc://localhost,1433/AlluresDb?driver=ODBC%20Driver%2017%20for%20SQL%20Server&;Trusted_Connection=yes"
ProductEngine = create_engine(ALLURES_DB_URL)
ProductSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=ProductEngine)

# 🔧 Подключение к ReviewDb (отзывы)
REVIEW_DB_URL = "mssql+pyodbc://localhost,1433/ReviewDb?driver=ODBC%20Driver%2017%20for%20SQL%20Server&;Trusted_Connection=yes"
ReviewEngine = create_engine(REVIEW_DB_URL)
ReviewSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=ReviewEngine)

def main():
    product_db = ProductSessionLocal()
    review_db = ReviewSessionLocal()

    try:
        print("\n🔍 Продукты из AlluresDb:")
        products = product_db.query(ProductDb).limit(5).all()

        if not products:
            print("⚠️ Нет продуктов в базе данных AlluresDb.")
        else:
            for p in products:
                print(f"\n✅ ID: {p.id} | Название: {p.name} | Категория: {p.category_name}")
                print(f"📃 Описание: {p.description}")

                # Ищем отзывы по продукту
                reviews = review_db.query(Review).filter(Review.product_id == p.id).all()
                if reviews:
                    print("🗣 Отзывы:")
                    for r in reviews:
                        print(f"  • [{r.sentiment.upper()}] {r.text}")
                else:
                    print("🕳 Отзывов нет.")
    finally:
        product_db.close()
        review_db.close()

if __name__ == "__main__":
    main()
