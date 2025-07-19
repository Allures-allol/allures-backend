#services/profile_service/main.py
import sys
import os
import common.utils.env_loader

# Добавление корневого пути (чтобы импортировать общие модули)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))  # доступ к /services и /common

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from dotenv import load_dotenv

from services.profile_service.routers import company, schedule
from common.db.session import get_db
from common.config.settings import settings

load_dotenv()

app = FastAPI(title="Profile Service")

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
app.include_router(company.router, prefix="/company", tags=["Company Profile"])
app.include_router(schedule.router, prefix="/schedule", tags=["Work Schedule"])

# db_url = os.getenv("MAINDB_URL")
# print(" MAINDB_URL:", db_url)

# Проверка подключения к PostgreSQL
@app.on_event("startup")
def startup_event():
    db_gen = get_db()
    db = next(db_gen)
    try:
        db.execute(text("SELECT 1"))
        print(" PostgreSQL подключение успешно (Profile Service)")
    except Exception as e:
        print(f" Ошибка подключения к PostgreSQL: {e}")
    finally:
        db.close()

# Корень
@app.get("/")
def read_root():
    return {"message": "Profile Service is running"}

# uvicorn services.profile_service.main:app --reload --port 8004