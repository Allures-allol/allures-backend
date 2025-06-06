# services/common/db/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

# Чтение строки подключения из .env.review
ALLURES_DB_URL = os.getenv("ALLURES_DB_URL")

engine = create_engine(ALLURES_DB_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

