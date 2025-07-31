#main.py product_service
import sys
import os
# import common.utils.env_loader

# Добавление корневого пути (чтобы импортировать общие модули)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))  # доступ к /services и /common

from fastapi import FastAPI
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from common.models.products import Product
from common.models.categories import Category


from common.db.session import get_db
from common.config.settings import settings

from services.product_service.api.routes import router as product_router
# from services.product_service.api import image_classifier_router
from services.review_service.api.routes import router as review_router
# from graphql_app.schema import schema as review_schema
# from strawberry.fastapi import GraphQLRouter

# Загрузка .env переменных
load_dotenv()

app = FastAPI(title="Product Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://api.alluresallol.com",
        "https://alluresallol.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Проверка: вывод URL подключения
print("▶ MAINDB_URL из settings:", settings.MAINDB_URL)

# Подключаем REST маршруты
app.include_router(product_router, prefix="/products", tags=["Products"])

app.include_router(review_router, prefix="/reviews", tags=["Reviews"])

# app.include_router(image_classifier_router.router, prefix="/product", tags=["AI classifier"])

# db_url = os.getenv("MAINDB_URL")
# print(" MAINDB_URL:", db_url)

# Проверка подключения к БД
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

# Загрузка модели при старте
# from services.product_service.api.image_classifier_router import download_model_if_needed

# @app.on_event("startup")
# def download_model_startup():
#     try:
#         download_model_if_needed()
#         print("✅ Модель успешно загружена или уже существует")
#     except Exception as e:
#         print("❌ Ошибка загрузки модели:", str(e))

@app.get("/")
def root():
    return {"message": "Product Service is running"}

@app.get("/check-db")
def check_db():
    db_gen = get_db()
    db = next(db_gen)
    try:
        result = db.execute(text("SELECT * FROM products LIMIT 1")).fetchall()
        return {"products_count": len(result)}
    except Exception as e:
        return {"error": str(e)}
    finally:
        db.close()
# GraphQL (в будущем можно раскомментировать)
# graphql_app = GraphQLRouter(review_schema)
# app.include_router(graphql_app, prefix="/graphql_app")

# uvicorn services.product_service.main:app --reload --port 8000