import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router as product_router
from common.db.session import get_db
from sqlalchemy import text
from common.config.settings import settings

load_dotenv()

app = FastAPI(title="Product Service")

# Добавляем маршруты
app.include_router(product_router, prefix="/products", tags=["products"])

# CORS Middleware (можно на раннем этапе)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # локальный React
        "http://127.0.0.1:3000",
        "https://allures-allol.com",  # будущее прод-домен
        "https://allures-frontend.vercel.app",  # если деплой через Vercel
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Главная страница
@app.get("/")
def root():
    return {"message": "Hello from Product Service"}

# Проверка подключения к MSSQL
@app.on_event("startup")
def startup_event():
    db_gen = get_db()
    db = next(db_gen)

    try:
        db.execute(text("SELECT 1"))
        print("✅ MSSQL подключение успешно (Product Service)")
    except Exception as e:
        print(f"❌ Ошибка подключения к MSSQL: {e}")
    finally:
        db.close()

print("✅ ALLURES_DB_URL:", settings.ALLURES_DB_URL)
