#main.py для discount_service
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, Depends
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from common.db.session import get_db
from common.config.settings import settings
from routers import discount

load_dotenv()

app = FastAPI(title="Discount Service")

app.include_router(discount.router, prefix="/discounts", tags=["Discounts"])

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
    return {"message": "Discount Service is running"}

# uvicorn services.discount_service.main:app --reload --port 8006