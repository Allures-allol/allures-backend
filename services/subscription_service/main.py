# services/subscription_service/main.py
from __future__ import annotations
import os
import sys

# доступ к /services и /common
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from dotenv import load_dotenv

from common.db.session import get_db
from services.subscription_service.routers.subscription_routers import router as subscription_router

load_dotenv()

USE_ROOT_PATH = os.getenv("SUBSCRIPTION_USE_ROOT_PATH", "0") == "1"

app = FastAPI(
    title="Subscription Service",
    root_path="/subscription" if USE_ROOT_PATH else "",  # PROD через gateway vs DEV локально
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

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

# РОУТЕР ПОДКЛЮЧАЕМ ОДИН РАЗ:
if USE_ROOT_PATH:
    # PROD: root_path даёт внешний /subscription
    app.include_router(subscription_router, tags=["subscription"])
else:
    # DEV: добавляем prefix локально
    app.include_router(subscription_router, prefix="/subscription", tags=["subscription"])

@app.get("/health", tags=["meta"])
def health():
    return {"status": "ok"}

@app.on_event("startup")
def startup_event():
    db_gen = get_db()
    db = next(db_gen)
    try:
        db.execute(text("SELECT 1"))
        print(" PostgreSQL подключение успешно (Subscription Service)")
    except Exception as e:
        print(f" Ошибка подключения к PostgreSQL: {e}")
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"message": "Subscription Service is running"}

# uvicorn services.subscription_service.main:app --reload --port 8011
