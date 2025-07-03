#main.py payment_service
import sys
import os
import common.utils.env_loader

# Добавление корневого пути (чтобы импортировать общие модули)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))  # доступ к /services и /common

from fastapi import FastAPI
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from common.models.payment import Payment
from common.db.session import get_db
from common.config.settings import settings
from services.payment_service.common.config.settings_payment import settings_payment
from services.payment_service.routers.payment import router as payment_router

# Загрузка .env
load_dotenv()

app = FastAPI(title="Payment Service")

# 🌍 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://allures-allol.com",
        "https://allures-frontend.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔗 Подключаем маршруты
app.include_router(payment_router, prefix="/payment", tags=["Payment Methods"])

# db_url = os.getenv("MAINDB_URL")
# print("🔗 MAINDB_URL:", db_url)

# ✅ Проверка подключения к PostgreSQL
@app.on_event("startup")
def startup_event():
    db_gen = get_db()
    db = next(db_gen)
    try:
        db.execute(text("SELECT 1"))
        print("✅ PostgreSQL подключение успешно (Payment Service)")
    except Exception as e:
        print(f"❌ Ошибка подключения к PostgreSQL: {e}")
    finally:
        db.close()

# 🌐 Корень
@app.get("/")
def read_root():
    return {"message": "Payment Service is running"}


# uvicorn services.payment_service.main:app --reload --port 8005