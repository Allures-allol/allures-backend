#services/auth_service/main.py
import sys
import os
import common.utils.env_loader

# Добавление корневого пути (чтобы импортировать общие модули)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))  # доступ к /services и /common

from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from typing import List
from sqlalchemy import text
from common.models.user import User
from common.models.uploads import Upload
from common.db.session import get_db
from common.config.settings import settings
from services.auth_service.routers import auth
from services.auth_service.utils.security import create_access_token
from services.auth_service.schemas.user import UserOut, ForgotPassword, ResetPassword
from services.auth_service.crud.user import get_all_users, forgot_password, reset_password

# Загрузка .env
load_dotenv()

app = FastAPI(title="Authorization Service")

# 🌍 CORS
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

# 🔗 Роутеры
app.include_router(auth.router, prefix="/auth", tags=["auth"])
#
# db_url = os.getenv("MAINDB_URL")
# print("🔗 MAINDB_URL:", db_url)

# ✅ Проверка подключения к PostgreSQL
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

# 🌐 Корень
@app.get("/")
def read_root():
    return {"message": "Authorization Service is running"}

# 👥 Получить всех пользователей
@app.get("/auth/users", response_model=List[UserOut])
def list_users(db: Session = Depends(get_db)):
    return get_all_users(db)

# 📩 Восстановление пароля
@app.post("/auth/forgot-password")
def forgot(user_data: ForgotPassword, db: Session = Depends(get_db)):
    return forgot_password(db, user_data.email)

# 🔐 Сброс пароля
@app.post("/auth/reset-password")
def reset(user_data: ResetPassword, db: Session = Depends(get_db)):
    return reset_password(db, user_data.email, user_data.new_password)


# uvicorn services.auth_service.main:app --reload --port 8003