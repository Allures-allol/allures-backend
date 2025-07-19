# test_review_product_proxy.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os
from common.models.products import Product

load_dotenv()

MAINDB_URL = os.getenv("MAINDB_URL")
if not MAINDB_URL:
    raise ValueError(" MAINDB_URL не задан в .env")

engine = create_engine(MAINDB_URL, echo=False, future=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Функция-тест для pytest
def test_products_query():
    db = SessionLocal()
    try:
        products = db.query(Product).limit(1).all()
        assert isinstance(products, list)
        print(" Успешный запрос к таблице products.")
    except Exception as e:
        assert False, f" Ошибка запроса к products: {e}"
    finally:
        db.close()
