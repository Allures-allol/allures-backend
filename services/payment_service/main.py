#main.py payment_service
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, Depends
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from common.db.session import get_db
from sqlalchemy import text
from common.config.settings import settings
from services.payment_service.common.config.settings_payment import settings_payment
from services.payment_service.routers.payment import router as payment_router
from routers import payment

load_dotenv()

app = FastAPI(title="Payment Service")

app.include_router(payment.router, prefix="/payment", tags=["Payment Methods"])

# CORS Middleware
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

@app.get("/")
def read_root():
    return {"message": "Payment Service is running"}

# uvicorn services.payment_service.main:app --reload --port 8005