# services/common/db/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

MAINDB_URL = os.getenv("MAINDB_URL")

engine = create_engine(MAINDB_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

