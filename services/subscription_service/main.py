#services/subscription_service/main.py
# services/subscription_service/main.py

import sys
import os
import common.utils.env_loader  # noqa: F401

# Добавление корневого пути (для доступа к общим модулям)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from dotenv import load_dotenv

from services.subscription_service.routers.subscription_routers import router as subscription_router
from common.db.session import get_db

# Подгружаем .env (если нужно — MAINDB_URL, JWT и т.п.)
load_dotenv()

# --- Инициализация FastAPI ---
app = FastAPI(
    title="Subscription Service",
    root_path="/subscription",         # корневой префикс сервиса
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# --- CORS ---
ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://api.alluresallol.com",
    "https://alluresallol.com",
    "https://allures-frontend.vercel.app",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Роутеры ---
# ВАЖНО: без дополнительного prefix="/subscription", так как root_path уже задан.
app.include_router(subscription_router, tags=["subscription"])

# --- Health check ---
@app.get("/health", tags=["meta"])
def health():
    return {"status": "ok"}

# --- Проверка подключения к PostgreSQL ---
@app.on_event("startup")
def startup_event():
    db_gen = get_db()
    db = next(db_gen)
    try:
        db.execute(text("SELECT 1"))
        print("✅ PostgreSQL подключение успешно (Subscription Service)")
    except Exception as e:
        print(f"❌ Ошибка подключения к PostgreSQL: {e}")
    finally:
        db.close()

# --- Корень ---
@app.get("/")
def read_root():
    return {"message": "Subscription Service is running"}

# --- Запуск через uvicorn ---
# Локально:
# uvicorn services.subscription_service.main:app --reload --port 8011
