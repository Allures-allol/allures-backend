# services/admin_service/main.py
import sys
import os
from dotenv import load_dotenv

# доступ к /services и /common
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from common.config.settings import settings
from common.db.base import Base
from common.db.session import engine, get_db
from common.models.admin import AdminUser  # важно импортировать модель до create_all

from services.admin_service.routers import admin_router
from services.admin_service.routers.admin_delete import router as admin_delete_router

load_dotenv()

USE_ROOT_PATH = os.getenv("ADMIN_USE_ROOT_PATH", "0") == "1"

app = FastAPI(
    title="Admin Service",
    root_path="/admin" if USE_ROOT_PATH else "",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://api.alluresallol.com",
    "https://alluresallol.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Маршруты:
# Если root_path уже "/admin", то внутр. пути должны начинаться с "/" или "/delete".
# Если root_path пуст, добавляем prefix="/admin", чтобы получить /admin/…
if USE_ROOT_PATH:
    # внешние пути: /admin/...
    app.include_router(admin_router.router, tags=["Admin"])             # /users, /login, ...
    app.include_router(admin_delete_router, tags=["Admin Deletes"])     # /delete/...
else:
    # внешние пути: /admin/...
    app.include_router(admin_router.router, prefix="/admin", tags=["Admin"])
    app.include_router(admin_delete_router, tags=["Admin Deletes"])

@app.on_event("startup")
def startup_event():
    # гарантируем, что таблицы созданы
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        print(f" Base.metadata.create_all: {e}")

    # проверка подключения к БД
    db_gen = get_db()
    db = next(db_gen)
    try:
        db.execute(text("SELECT 1"))
        print(" PostgreSQL подключение успешно (Admin Service)")
    except Exception as e:
        print(f" Ошибка подключения к PostgreSQL: {e}")
    finally:
        db.close()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/")
def root():
    return {"message": "Admin Service is running"}

# запуск локально:
# uvicorn services.admin_service.main:app --reload --port 8010


# uvicorn services.admin_service.main:app --reload --port 8010
