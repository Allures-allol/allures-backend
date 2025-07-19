#services/admin_service/main.py
import sys
import os
import common.utils.env_loader

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

# Путь к общим модулям
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
from common.models.user import User
from common.models.uploads import Upload
from services.admin_service.routers import admin_router
from common.db.session import get_db
from dotenv import load_dotenv

# Загрузка .env
load_dotenv()

app = FastAPI(title="Admin Service")

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

# Роуты
app.include_router(admin_router.router, prefix="/admin", tags=["Admin"])

# db_url = os.getenv("MAINDB_URL")
# print(" MAINDB_URL:", db_url)

# Проверка подключения к БД
@app.on_event("startup")
def startup_event():
    db_gen = get_db()
    db = next(db_gen)
    try:
        db.execute(text("SELECT 1"))
        print(" PostgreSQL подключение успешно (Admin Service)")
    except Exception as e:
        print(f" Ошибка подключения к PostgreSQL: {e}")
    finally:
        db.close()

@app.get("/")
def root():
    return {"message": "Admin Service is running"}

# uvicorn services.admin_service.main:app --reload --port 8010