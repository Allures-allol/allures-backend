# services/payment_service/main.py
import sys
import os
from dotenv import load_dotenv

# Доступ к /services и /common
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from common.config.settings import settings
from common.db.session import get_db
from services.payment_service.routers.payment import router as payment_router

load_dotenv()

app = FastAPI(
    title="Payment Service",
    root_path="/payment",     # внешний префикс, как в review
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Можно читать из .env (settings.extra=allow), но оставлю явный список
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

# Важно: без prefix — root_path уже добавит /payment снаружи
app.include_router(payment_router, tags=["Payment"])

@app.on_event("startup")
def on_startup():
    # Проверка подключения к БД через общий settings.MAINDB_URL
    db_gen = get_db()
    db = next(db_gen)
    try:
        db.execute(text("SELECT 1"))
        print(" PostgreSQL подключение успешно (Payment Service)")
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
    return {"message": "Payment Service is running"}

# запуск локально:
# uvicorn services.payment_service.main:app --reload --port 8005
