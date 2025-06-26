#корень /main.py
import sys
import os
# Добавление корневого пути (чтобы импортировать общие модули)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))  # доступ к /services и /common

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from sqlalchemy import text

from common.db.session import get_db

# Импорт роутеров из всех микросервисов
from services.product_service.api.routes import router as product_router
from services.review_service.api.routes import router as review_router
from services.sales_service.api.routes import router as sales_router
from services.payment_service.routers.payment import router as payment_router
from services.discount_service.routers.discount import router as discount_router
from services.auth_service.routers.auth import router as auth_router
from services.dashboard_service.routers.dashboard import router as dashboard_router

# Загрузка переменных окружения
load_dotenv()

app = FastAPI(title="Allures Backend")

# 🔗 Подключение всех роутеров
app.include_router(product_router, prefix="/products", tags=["Products"])
app.include_router(review_router, prefix="/reviews", tags=["Reviews"])
app.include_router(sales_router, prefix="/sales", tags=["Sales"])
app.include_router(payment_router, prefix="/payment", tags=["Payment"])
app.include_router(discount_router, prefix="/discounts", tags=["Discounts"])
app.include_router(auth_router, prefix="/auth", tags=["Auth"])
app.include_router(dashboard_router, prefix="/dashboard", tags=["Dashboard"])

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

# ✅ Проверка подключения к PostgreSQL
@app.on_event("startup")
def startup_event():
    db_gen = get_db()
    db = next(db_gen)
    try:
        db.execute(text("SELECT 1"))
        print("✅ PostgreSQL подключение успешно (Allures Backend)")
    except Exception as e:
        print(f"❌ Ошибка подключения к PostgreSQL: {e}")
    finally:
        db.close()

# 🌐 Корень
@app.get("/")
def root():
    return {"message": "Hello from Allures Backend"}

# uvicorn main:app --reload --port 8008