# services/product_service/test_product_proxy.py

import sys
import os
from sqlalchemy.orm import Session

# ✅ Добавляем корень проекта в sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from common.db.product_connection import ProductSessionLocal
from services.review_service.models.product_proxy import ProductDb

def main():
    db: Session = ProductSessionLocal()
    try:
        print("🧪 Загружаем продукты из AlluresDb...")

        products = db.query(ProductDb).limit(5).all()
        if not products:
            print("⚠️ Нет продуктов в базе данных.")
        else:
            for p in products:
                print(f"✅ ID: {p.id} | Название: {p.name} | Категория: {p.category_name} | Описание: {p.description}")
    finally:
        db.close()

if __name__ == "__main__":
    main()
