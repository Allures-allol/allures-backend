import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from common.db.session import get_db
from common.config.settings import settings

from services.auth_service.utils.security import create_access_token
from services.auth_service.schemas.user import UserOut, UserCreate, ForgotPassword, ResetPassword
from services.auth_service.crud.user import get_all_users, authenticate_user, create_user, forgot_password, reset_password
from typing import List

load_dotenv()

app = FastAPI(title="Authorization Service")

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
    return {"message": "Authorization Service is running"}

@app.get("/auth/users", response_model=List[UserOut])
def list_users(db: Session = Depends(get_db)):
    return get_all_users(db)

@app.post("/auth/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid credentials")
    token = create_access_token(user.login)
    return {"access_token": token, "token_type": "bearer"}

@app.post("/auth/register")
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    user = create_user(db, user_data)
    return user

@app.post("/auth/forgot-password")
def forgot(user_data: ForgotPassword, db: Session = Depends(get_db)):
    return forgot_password(db, user_data.email)

@app.post("/auth/reset-password")
def reset(user_data: ResetPassword, db: Session = Depends(get_db)):
    return reset_password(db, user_data.email, user_data.new_password)
