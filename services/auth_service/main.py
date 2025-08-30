# services/auth_service/main.py

import sys
import os

# загружаем .env как можно раньше
from dotenv import load_dotenv

load_dotenv()

# опциональный общий загрузчик, если он у тебя что-то делает (оставил как было)
import common.utils.env_loader  # noqa: F401

# Добавление корневого пути (для доступа к общим модулям)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from services.auth_service.routers import auth as auth_router
from services.auth_service.routers import profile as profile_router
from common.db.session import get_db


# ---- Диагностика ключевых переменных ----
jwt_secret = os.getenv("JWT_SECRET")
if jwt_secret:
    print(f"🔐 JWT_SECRET загружен: {jwt_secret[:10]}... (длина = {len(jwt_secret)})")
else:
    print("❌ JWT_SECRET НЕ НАЙДЕН! Проверь .env файл")

# root_path используем ТОЛЬКО если приложение висит за префиксом у ревёрс-прокси
# (например, Nginx отдаёт сервис по /auth). Иначе оставляем пустым.
_use_root = os.getenv("AUTH_USE_ROOT_PATH", "0").strip().lower() in ("1", "true", "yes")
ROOT_PATH = "/auth" if _use_root else ""

# --- Инициализация FastAPI ---
app = FastAPI(
    title="Auth Service",
    root_path=ROOT_PATH,          # << ключевой момент
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# --- CORS ---
# Можно указывать список доменов через запятую в .env: CORS_ALLOWED_ORIGINS=...,...
_cors_env = os.getenv("CORS_ALLOWED_ORIGINS", "")
if _cors_env.strip():
    ALLOWED_ORIGINS = [o.strip() for o in _cors_env.split(",") if o.strip()]
else:
    # дефолтный набор для локалки
    ALLOWED_ORIGINS = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://alluresallol.com",
        "https://api.alluresallol.com",
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,   # можно True — вдруг решишь ставить cookie в будущем
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Роутеры ---
# ВНИМАНИЕ: сам роутер auth имеет prefix="/auth", поэтому здесь root_path НЕ должен быть "/auth" в DEV.
# Мы это уже учли через AUTH_USE_ROOT_PATH.
app.include_router(auth_router.router)      # tags заданы внутри роутера
app.include_router(profile_router.router)   # профиль оставлен как есть

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
@app.get("/", tags=["meta"])
def read_root():
    return {"message": "Authorization Service is running."}

# Запуск:
# uvicorn services.auth_service.main:app --reload --port 8003
