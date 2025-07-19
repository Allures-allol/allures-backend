# test_connection.py
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from common.config.settings import settings

# Загружаем переменные окружения из .env
load_dotenv()

# Создание движка и сессии
engine = create_engine(settings.MAINDB_URL, future=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def test_db_connection():
    """
    Проверка подключения к базе данных PostgreSQL.
    Выполняется простой запрос SELECT 1.
    """
    db = None
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        print(" Успешное подключение к базе данных!")
    except Exception as e:
        print(" Ошибка подключения:", e)
        assert False, f"Ошибка подключения: {e}"
    finally:
        if db:
            db.close()
