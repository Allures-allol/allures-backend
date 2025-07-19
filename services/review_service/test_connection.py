# services/review_service/models/recommendation.py
import os
from pathlib import Path
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Явно загружаем .env из корня проекта
env_path = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(dotenv_path=env_path)

# Подключение к базе
MAINDB_URL = os.getenv("MAINDB_URL")
if not MAINDB_URL:
    raise ValueError("MAINDB_URL не определён. Проверь .env путь или переменную.")

engine = create_engine(MAINDB_URL, future=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def test_review_db_connection():
    db = None
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        print(" Успешное подключение к базе данных из review_service!")
    except Exception as e:
        print(" Ошибка подключения:", e)
        assert False, f"Ошибка подключения: {e}"
    finally:
        if db:
            db.close()

