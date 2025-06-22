#main.py product_service
from fastapi import FastAPI
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from common.db.session import get_db
from common.config.settings import settings
from services.product_service.api.routes import router as product_router
from services.review_service.api.routes import router as review_router
# from graphql_app.schema import schema as review_schema
# from strawberry.fastapi import GraphQLRouter

# Загрузка .env переменных
load_dotenv()

app = FastAPI(title="Product Service")

# 🔗 Подключаем REST маршруты
app.include_router(product_router, prefix="/products", tags=["Products"])
app.include_router(review_router, prefix="/reviews", tags=["Reviews"])

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
        print("✅ PostgreSQL подключение успешно (Product Service)")
    except Exception as e:
        print(f"❌ Ошибка подключения к PostgreSQL: {e}")
    finally:
        db.close()

# 🌐 Корень
@app.get("/")
def root():
    return {"message": "Product Service is running"}

# GraphQL (в будущем можно раскомментировать)
# graphql_app = GraphQLRouter(review_schema)
# app.include_router(graphql_app, prefix="/graphql_app")

# uvicorn services.product_service.main:app --reload --port 8000