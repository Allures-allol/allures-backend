#services/auth_service/main.py
import sys
import os
import common.utils.env_loader

# Добавление корневого пути (для доступа к общим модулям)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from dotenv import load_dotenv

from common.db.session import get_db
from services.auth_service.routers import auth
from common.config.settings import settings

load_dotenv()

app = FastAPI(title="Authorization Service")

# 🌍 CORS — для фронта и локальной разработки
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

# 🔗 Подключение роутеров
app.include_router(auth.router, prefix="/auth", tags=["auth"])

# ✅ Проверка подключения к PostgreSQL
@app.on_event("startup")
def startup_event():
    db_gen = get_db()
    db = next(db_gen)
    try:
        db.execute(text("SELECT 1"))
        print("✅ PostgreSQL подключение успешно (Authorization Service)")
    except Exception as e:
        print(f"❌ Ошибка подключения к PostgreSQL: {e}")
    finally:
        db.close()

# 🌐 Корневой эндпоинт
@app.get("/")
def read_root():
    return {"message": "Authorization Service is running"}

# uvicorn services.auth_service.main:app --reload --port 8003