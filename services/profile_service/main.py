# services/profile_service/main.py

import sys
import os
from dotenv import load_dotenv

# доступ к /services и /common
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from common.config.settings import settings
from common.db.session import get_db

# ⬇️ подключаем роутеры
from services.profile_service.routers.company import router as company_router
from services.profile_service.routers.schedule import router as schedule_router

load_dotenv()

app = FastAPI(
    title="Profile Service",
    root_path="/profile",   # внешний префикс (снаружи будет /profile/...)
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

# ⬇️ подключаем БЕЗ конфликтов (внутренние prefix работают вместе с root_path)
app.include_router(company_router, prefix="/companies", tags=["Companies"])
app.include_router(schedule_router, prefix="/schedules", tags=["Schedules"])

@app.on_event("startup")
def on_startup():
    db_gen = get_db()
    db = next(db_gen)
    try:
        db.execute(text("SELECT 1"))
        print(" PostgreSQL подключение успешно (Profile Service)")
        print(f" DB_ECHO={settings.DB_ECHO}")
    except Exception as e:
        print(f" Ошибка подключения к PostgreSQL: {e}")
    finally:
        db.close()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/")
def root():
    return {"message": "Profile Service is running"}

# локально:
# uvicorn services.profile_service.main:app --reload --port 8004
