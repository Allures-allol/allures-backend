import os
from common.config.settings import settings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import time

load_dotenv()

MAINDB_URL = settings.MAINDB_URL  # или "LOCAL_DB_URL"

MAX_RETRIES = 3
RETRY_DELAY = 5

def create_database_engine_with_retries():
    for attempt in range(MAX_RETRIES):
        try:
            engine = create_engine(MAINDB_URL, echo=True)
            return engine
        except Exception as e:
            print(f"[{attempt + 1}/{MAX_RETRIES}] Ошибка подключения: {e}")
            if attempt < MAX_RETRIES - 1:
                print(f"Повтор через {RETRY_DELAY} секунд...")
                time.sleep(RETRY_DELAY)
            else:
                raise

engine = create_database_engine_with_retries()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

