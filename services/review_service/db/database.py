from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from services.review_service.common.config.settings_review import settings_review

# Строка подключения — локально (Windows Auth)
SQLALCHEMY_DATABASE_URL = settings_review.ALLURES_DB_URL #Change to LOCAL_DB_URL after

# Создание движка SQLAlchemy
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Создание сессии
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Базовый класс для моделей
Base = declarative_base()

# Инициализация базы данных — создание всех таблиц
def init_db():
    from services.review_service.models.review import Review  # Важно: импорт внутри
    Base.metadata.create_all(bind=engine)

# Получение сессии для использования в Depends
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
