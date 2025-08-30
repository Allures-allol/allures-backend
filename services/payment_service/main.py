# services/payment_service/main.py
import os
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

# доступ к /services и /common
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from dotenv import load_dotenv
from common.db.session import get_db
from common.config.settings import settings
from services.payment_service.routers.payment import router as payment_router

load_dotenv()

USE_ROOT_PATH = os.getenv("PAYMENT_USE_ROOT_PATH", "0") == "1"

app = FastAPI(
    title="Payment Service",
    root_path="/payment" if USE_ROOT_PATH else "",
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

# Роуты платежей (NowPayments + Monobank)
if USE_ROOT_PATH:
    app.include_router(payment_router, tags=["payments"])
else:
    app.include_router(payment_router, prefix="/payment", tags=["payments"])

@app.get("/health")
def health():
    return {"status": "ok"}

@app.on_event("startup")
def startup_event():
    db_gen = get_db()
    db = next(db_gen)
    try:
        db.execute(text("SELECT 1"))
        print(" PostgreSQL подключение успешно (Payment Service)")
    except Exception as e:
        print(f" Ошибка подключения к PostgreSQL: {e}")
    finally:
        db.close()

@app.get("/")
def root():
    return {"message": "Payment Service is running"}


# запуск локально:
# uvicorn services.payment_service.main:app --reload --port 8005
