# test_sales_service.py
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from common.models.sales import Sales

load_dotenv()

MAINDB_URL = os.getenv("MAINDB_URL")

if not MAINDB_URL:
    raise ValueError(" Переменная MAINDB_URL не найдена. Проверь .env файл.")

engine = create_engine(MAINDB_URL, echo=False, future=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Pytest-тест для проверки подключения и выборки
def test_sales_query():
    db = SessionLocal()
    try:
        sales = db.query(Sales).limit(1).all()
        assert isinstance(sales, list)
        print(" Данные успешно получены из таблицы sales.")
    except Exception as e:
        assert False, f" Ошибка при выполнении запроса к sales: {e}"
    finally:
        db.close()
