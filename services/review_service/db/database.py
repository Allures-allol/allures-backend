# services/review_service/db/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from services.review_service.common.config.settings_review import settings_review

# Создание движка подключения
engine = create_engine(
    settings_review.MAINDB_URL,
    echo=True,  # Вкл. лог SQL-запросов — можно отключить на проде
    future=True  # Рекомендуется для SQLAlchemy 1.4+
)

# Создание локальной сессии
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    future=True
)

# ✅ Генератор сессии для Depends
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

