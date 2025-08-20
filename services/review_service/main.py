# services/review_service/main.py
import sys
import os
# import common.utils.env_loader

# Добавление корневого пути (для доступа к /services и /common)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from common.db.base import Base
from common.db.session import engine, get_db
from common.config.settings import settings

from common.models.products import Product
from common.models.categories import Category
from common.models.payment import Payment
from common.models.subscriptions import Subscription, UserSubscription
from services.review_service.models.recommendation import Recommendation
from services.review_service.models.review import Review
from services.review_service.api.routes import router as reviews_router
from dotenv import load_dotenv

# Загрузка .env
load_dotenv()

app = FastAPI(
    title="Review Service",
   #root_path="/reviews",        # ВНЕШНИЙ префикс
    docs_url="/docs",            # снаружи: /reviews/docs
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

# РОУТЕР БЕЗ prefix — root_path уже добавит /reviews снаружи
app.include_router(reviews_router, tags=["Reviews"])

@app.on_event("startup")
def on_startup():
    # если нужны таблицы для review/recommendation — создаём
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        print(f" Base.metadata.create_all: {e}")

    db_gen = get_db()
    db = next(db_gen)
    try:
        db.execute(text("SELECT 1"))
        print(" PostgreSQL подключение успешно (Review Service)")
    except Exception as e:
        print(f" Ошибка подключения к PostgreSQL: {e}")
    finally:
        db.close()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/")
def root():
    return {"message": "Review Service is running"}


# uvicorn services.review_service.main:app --reload --port 8002
