# services/product_service/main.py

import os
import sys
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session

# доступ к /services и /common
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from dotenv import load_dotenv
from common.db.session import get_db
from common.config.settings import settings
from common.models.products import Product as ProductModel

from services.product_service.api.routes import router as product_router
from services.product_service.api.cart_orders import router as cart_orders_router

load_dotenv()

USE_ROOT_PATH = os.getenv("PRODUCT_USE_ROOT_PATH", "0") == "1"

openapi_tags = [
    {"name": "products", "description": "Product catalog, categories, reviews proxy"},
    {"name": "cart-orders", "description": "Cart and orders tied to user"},
    {"name": "system", "description": "Health checks and debug"},
]

app = FastAPI(
    title="Product Service",
    root_path="/product" if USE_ROOT_PATH else "",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    openapi_tags=openapi_tags,
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
# 1) СНАЧАЛА — БИЗНЕС-РОУТЕРЫ
# ==============================
if USE_ROOT_PATH:
    app.include_router(product_router, tags=["products"])
    app.include_router(cart_orders_router, tags=["cart-orders"])
else:
    app.include_router(product_router, prefix="/product", tags=["products"])
    app.include_router(cart_orders_router, prefix="/product", tags=["cart-orders"])

print(" MAINDB_URL из settings:", settings.MAINDB_URL)

# ==============================
# 2) СТАРТ И ХЕЛСЧЕКИ/ДЕБАГ
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

@app.get("/health", include_in_schema=False, tags=["system"])
def health():
    return {"status": "ok"}

@app.get("/", tags=["system"])
def root():
    return {"message": "Product Service is running"}

@app.get("/check-db", tags=["system"])
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

@app.get("/__debug/db_url", tags=["system"])
def debug_db_url():
    return {"MAINDB_URL": os.getenv("MAINDB_URL", "(not set)")}

@app.get("/__debug/products_count", tags=["system"])
def debug_products_count(db: Session = Depends(get_db)):
    return {"count": db.query(ProductModel).count()}

# uvicorn services.product_service.main:app --reload --port 8000