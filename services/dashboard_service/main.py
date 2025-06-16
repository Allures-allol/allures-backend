#services/dashboard_service/main.py
# Маршруты для вывода всех пользователей, отзывов, продаж, скидок
import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from services.dashboard_service.routers import dashboard
from common.config.settings import settings
from common.db.session import get_db

app = FastAPI(title="Dashboard Service")

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

app.include_router(dashboard.router, prefix="/dashboard")

@app.get("/")
def root():
    return {"message": "Dashboard Service is running"}

# uvicorn services.dashboard_service.main:app --reload --port 8007
