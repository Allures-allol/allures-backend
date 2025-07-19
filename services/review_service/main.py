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
from common.models.products import Product
from common.models.categories import Category

from common.models.payment import Payment
from common.models.subscriptions import Subscription, UserSubscription
from common.db.base import Base
from common.db.session import engine, get_db
from services.review_service.api.routes import router
from services.review_service.models.recommendation import Recommendation
from services.review_service.models.review import Review
from dotenv import load_dotenv

# Загрузка .env
load_dotenv()

app = FastAPI(title="Review Service")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://api.alluresallol.com",
        "https://alluresallol.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Здесь была ошибка — теперь исправлено
app.include_router(router, prefix="/reviews", tags=["Reviews"])

# db_url = os.getenv("MAINDB_URL")
# print(" MAINDB_URL:", db_url)

# Создание таблиц при старте
@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    db_gen = get_db()
    db = next(db_gen)
    try:
        db.execute(text("SELECT 1"))
        print("PostgreSQL подключение успешно (Review Service)")
    except Exception as e:
        print(f"Ошибка подключения к PostgreSQL: {e}")
    finally:
        db.close()

# Корень
@app.get("/")
def root():
    return {"message": "Review Service is running"}


# uvicorn services.review_service.main:app --reload --port 8002