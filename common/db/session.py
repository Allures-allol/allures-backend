# common/db/session.py
from __future__ import annotations

import time
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from common.config.settings import settings

DB_URL = settings.effective_db_url
if not DB_URL:
    raise RuntimeError(

        "Не задан URL БД. Укажи DATABASE_URL (предпочтительно) "
        "или MAINDB_URL в .env / переменных окружения."
    )

MAX_RETRIES = 3
RETRY_DELAY = 5  # сек


def create_database_engine_with_retries():
    last_err = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            engine = create_engine(
                DB_URL,
                pool_pre_ping=True,
                future=True,
                echo=bool(settings.DB_ECHO),
            )
            return engine
        except Exception as e:
            last_err = e
            print(f"[{attempt}/{MAX_RETRIES}] Ошибка подключения к БД: {e}")
            if attempt < MAX_RETRIES:
                print(f"Повтор через {RETRY_DELAY} сек...")
                time.sleep(RETRY_DELAY)
    raise last_err


engine = create_database_engine_with_retries()

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    future=True,
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
