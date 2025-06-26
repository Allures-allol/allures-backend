import sys
import os
# Добавление корневого пути (чтобы импортировать общие модули)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))  # доступ к /services и /common

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from dotenv import load_dotenv

from services.sales_service.api.routes import router as sales_router
from common.db.session import get_db

# Загрузка переменных окружения
load_dotenv()

# Создание приложения
app = FastAPI(title="Sales Service")

# Подключение роутов
app.include_router(sales_router, tags=["sales"], prefix="/sales")

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",              # локальный React
        "http://127.0.0.1:3000",
        "https://allures-allol.com",          # прод-версия
        "https://allures-frontend.vercel.app" # Vercel
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Главная страница
@app.get("/")
def root():
    return {"message": "Hello from Sales Service"}

# Проверка подключения к PostgreSQL
@app.on_event("startup")
def startup_event():
    db_gen = get_db()
    db = next(db_gen)
    try:
        db.execute(text("SELECT 1"))
        print("✅ PostgreSQL подключение успешно (Sales Service)")
    except Exception as e:
        print(f"❌ Ошибка подключения к PostgreSQL: {e}")
    finally:
        db.close()

# uvicorn services.sales_service.main:app --reload --port 8001