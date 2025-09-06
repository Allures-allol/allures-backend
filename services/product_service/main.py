# main.py product_service
import os
import sys
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session

# Добавление корневого пути (чтобы импортировать общие модули)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))  # доступ к /services и /common

from dotenv import load_dotenv
from common.db.session import get_db
from common.config.settings import settings
from common.models.products import Product as ProductModel
from common.models.categories import Category as CategoryModel

# роутер продуктов
from services.product_service.api.routes import router as product_router

# Загрузка .env переменных
load_dotenv()

USE_ROOT_PATH = os.getenv("PRODUCT_USE_ROOT_PATH", "0") == "1"

app = FastAPI(
    title="Product Service",
    root_path="/product" if USE_ROOT_PATH else "",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# CORS
ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://api.alluresallol.com",
    "https://alluresallol.com",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==============================
# Health endpoint должен быть ОБЯЗАТЕЛЬНО до include_router
# ==============================
@app.get("/health", include_in_schema=False)
def health():
    return {"status": "ok"}

# ==============================
# Подключение роутера продуктов
# ==============================
if USE_ROOT_PATH:
    app.include_router(product_router, tags=["products"])
else:
    app.include_router(product_router, prefix="/product", tags=["products"])

print(" MAINDB_URL из settings:", settings.MAINDB_URL)

# ==============================
# Событие старта
# ==============================
@app.on_event("startup")
def startup_event():
    db_gen = get_db()
    db = next(db_gen)
    try:
        db.execute(text("SELECT 1"))
        print(" PostgreSQL подключение успешно (Product Service)")
    except Exception as e:
        print(f" Ошибка подключения к PostgreSQL: {e}")
    finally:
        db.close()

# ==============================
# Другие маршруты
# ==============================
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

@app.get("/__debug/db_url")
def debug_db_url():
    import os
    return {"MAINDB_URL": os.getenv("MAINDB_URL", "(not set)")}

@app.get("/__debug/products_count")
def debug_products_count(db: Session = Depends(get_db)):
    return {"count": db.query(ProductModel).count()}
