import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from fastapi import FastAPI
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from services.sales_service.api.routes import router as sales_router
from common.db.session import get_db
from sqlalchemy import text

load_dotenv()

app = FastAPI(title="Sales Service")

# Добавляем маршруты
app.include_router(sales_router, tags=["sales"], prefix="/sales")

# CORS Middleware (можно на раннем этапе)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # локальный React
        "http://127.0.0.1:3000",
        "https://allures-allol.com"  # прод-версия
        "https://allures-frontend.vercel.app",  # если деплой через Vercel
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Главная страница
@app.get("/")
def root():
    return {"message": "Hello from Sales Service"}

# Проверка подключения к MSSQL
@app.on_event("startup")
def startup_event():
    db_gen = get_db()
    db = next(db_gen)
    try:
        db.execute(text("SELECT 1"))
        print("✅ MSSQL подключение успешно (Sales Service)")
    except Exception as e:
        print(f"❌ Ошибка подключения к MSSQL: {e}")
    finally:
        db.close()


