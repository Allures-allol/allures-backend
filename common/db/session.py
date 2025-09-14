# common/db/session.py
from __future__ import annotations
import time
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError
from common.config.settings import settings

DB_URL = settings.effective_db_url
if not DB_URL:
    raise RuntimeError(
        "Не задан DATABASE_URL или MAINDB_URL. Проверь .env / переменные окружения."
    )

MAX_RETRIES = 3
RETRY_DELAY = 5  # сек
POOL_SIZE = 5
MAX_OVERFLOW = 0
POOL_RECYCLE = 300  # секунды, 5 минут

def create_engine_with_retries():
    last_err = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            engine = create_engine(
                DB_URL,
                future=True,
                echo=bool(settings.DB_ECHO),
                pool_pre_ping=True,      # проверяем соединение перед использованием
                pool_size=POOL_SIZE,
                max_overflow=MAX_OVERFLOW,
                pool_recycle=POOL_RECYCLE
            )
            return engine
        except Exception as e:
            last_err = e
            print(f"[{attempt}/{MAX_RETRIES}] Ошибка подключения к БД: {e}")
            if attempt < MAX_RETRIES:
                print(f"Повтор через {RETRY_DELAY} сек...")
                time.sleep(RETRY_DELAY)
    raise last_err

engine = create_engine_with_retries()
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)

def get_db():
    """
    Генератор сессии. Авто-закрытие + обработка OperationalError.
    Если пул перегружен или соединение упало — сбросим пул и переподключимся.
    """
    try:
        db = SessionLocal()
        yield db
    except OperationalError as e:
        print("[DB] OperationalError, переподключаемся:", e)
        global engine, SessionLocal
        engine.dispose()  # сброс всех соединений пула
        engine = create_engine_with_retries()
        SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
        db = SessionLocal()
        yield db
    finally:
        db.close()

def dispose_engine():
    """
    Явный сброс пула — можно вызвать при необходимости
    """
    global engine
    print("[DB] Disposing engine and clearing all connections...")
    engine.dispose()
