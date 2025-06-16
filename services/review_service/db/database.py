# services/review_service/db/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from services.review_service.common.config.settings_review import settings_review

engine = create_engine(settings_review.MAINDB_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
