# services/auth_service/main.py

import sys
import os
import common.utils.env_loader

# Добавление корневого пути (для доступа к общим модулям)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from dotenv import load_dotenv

from services.auth_service.routers import auth as auth_router
from services.auth_service.routers import profile as profile_router
from common.db.session import get_db

load_dotenv()

# Проверка JWT_SECRET (можно закомментировать позже)
secret = os.getenv("JWT_SECRET")
if secret:
    print(f"🔐 JWT_SECRET загружен: {secret[:10]}... (длина = {len(secret)})")
else:
    print("❌ JWT_SECRET НЕ НАЙДЕН! Проверь .env файл")

app = FastAPI(
    title="Authorization Service",
    version="1.0.0",
    swagger_ui_parameters={"persistAuthorization": True},
    root_path="/auth"    #ДОБАВИЛ НОВОЕ!!!!!!!!
)

# --- CORS ---
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

# --- Роутеры ---
app.include_router(auth_router.router, prefix="/auth", tags=["auth"])
app.include_router(profile_router.router, prefix="/profile", tags=["profile"])

# --- Health check ---
@app.get("/health", tags=["meta"])
def health():
    return {"status": "ok"}

# --- Проверка подключения к PostgreSQL ---
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

# --- Корень ---
@app.get("/")
def read_root():
    return {"message": "Authorization Service is running"}


# uvicorn services.auth_service.main:app --reload --port 8003
