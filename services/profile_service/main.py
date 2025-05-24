#main.py profile_service
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from routers import company, schedule
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from common.db.session import get_db
from common.config.settings import settings

load_dotenv()

app = FastAPI(title="Profile Service")

app.include_router(company.router, prefix="/company", tags=["Company Profile"])
app.include_router(schedule.router, prefix="/schedule", tags=["Work Schedule"])

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
    return {"message": "Profile Service is running"}
