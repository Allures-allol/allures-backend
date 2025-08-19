#services/subscription_service/main.py
import sys
import os
import common.utils.env_loader

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from services.subscription_service.routers.subscription_routers import router as subscription_router
from common.models.subscriptions import Subscription, UserSubscription
from common.models.payment import Payment

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
from common.db.session import get_db
from dotenv import load_dotenv

# Загрузка .env
load_dotenv()


app = FastAPI(title="Subscription Service")

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

app.include_router(subscription_router, prefix="/subscription", tags=["Subscription"])

# db_url = os.getenv("MAINDB_URL")
# print(" MAINDB_URL:", db_url)

@app.on_event("startup")
def startup_event():
    db_gen = get_db()
    db = next(db_gen)
    try:
        db.execute(text("SELECT 1"))
        print(" PostgreSQL подключение успешно (Subscription Service)")
    except Exception as e:
        print(f" Ошибка подключения к PostgreSQL: {e}")
    finally:
        db.close()

@app.get("/")
def root():
    return {"message": "Subscription Service is running"}

# uvicorn services.subscription_service.main:app --reload --port 8011