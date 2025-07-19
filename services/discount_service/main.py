#services/discount_service/main.py
import sys
import os
import common.utils.env_loader

from fastapi import FastAPI
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from common.db.session import get_db
from common.config.settings import settings
from services.discount_service.routers import discount

load_dotenv()

app = FastAPI(title="Discount Service")

app.include_router(discount.router, prefix="/discounts", tags=["Discounts"])

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

# db_url = os.getenv("MAINDB_URL")
# print(" MAINDB_URL:", db_url)

# Проверка подключения к PostgreSQL
@app.on_event("startup")
def startup_event():
    db_gen = get_db()
    db = next(db_gen)
    try:
        db.execute(text("SELECT 1"))
        print(" PostgreSQL подключение успешно (Discount Service)")
    except Exception as e:
        print(f" Ошибка подключения к PostgreSQL: {e}")
    finally:
        db.close()

# Корневая точка
@app.get("/")
def read_root():
    return {"message": "Discount Service is running"}

# uvicorn services.discount_service.main:app --reload --port 8006