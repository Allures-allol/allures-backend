# services/review_service/main.py
import os
import sys

# доступ к /services и /common
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from dotenv import load_dotenv

from common.db.base import Base
from common.db.session import engine, get_db
from common.models.categories import Category  # noqa: F401
from common.models.products import Product  # noqa: F401
from services.review_service.api.routes_reviews import reviews_router
from services.review_service.api.routes_recs import recs_router

load_dotenv()

USE_ROOT_PATH = os.getenv("REVIEW_USE_ROOT_PATH", "0") == "1"

openapi_tags = [
    {"name": "Reviews", "description": "CRUD по отзывам и модерация."},
    {"name": "Recommendations", "description": "Рекомендации и связанные операции."},
]

app = FastAPI(
    title="Review Service",
    version="1.0.0",
    root_path="/review" if USE_ROOT_PATH else "",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    openapi_tags=openapi_tags,
    debug=True,
)

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

# /review/... единый внешний префикс, группы задаются тегами
if USE_ROOT_PATH:
    app.include_router(reviews_router, tags=["Reviews"])
    app.include_router(recs_router, tags=["Recommendations"])
else:
    app.include_router(reviews_router, prefix="/review", tags=["Reviews"])
    app.include_router(recs_router, prefix="/review", tags=["Recommendations"])


@app.on_event("startup")
def on_startup() -> None:
    # создаём таблицы, если их ещё нет
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        print(f" Base.metadata.create_all: {e}")

    # простая проверка коннекта к БД
    db_gen = get_db()
    db = next(db_gen)
    try:
        db.execute(text("SELECT 1"))
        print(" PostgreSQL подключение успешно (Review Service)")
    except Exception as e:
        print(f" Ошибка подключения к PostgreSQL: {e}")
    finally:
        db.close()


@app.get("/health", include_in_schema=False)
def health():
    return {"status": "ok"}

@app.get("/", include_in_schema=False)
def root():
    return {"message": "Review Service is running"}

@app.get("/__debug/db")
def debug_db():
    import os
    return {
        "MAINDB_URL": os.getenv("MAINDB_URL", "(not set)"),
        "DATABASE_URL": os.getenv("DATABASE_URL", "(not set)"),
        "USE_ROOT_PATH": USE_ROOT_PATH,
    }

@app.get("/__debug/tables")
def debug_tables():
    from sqlalchemy import inspect
    insp = inspect(engine)
    return {"tables": insp.get_table_names()}

# uvicorn services.review_service.main:app --reload --port 8002
#  или с логами uvicorn services.review_service.main:app --reload --port 8002 --log-level debug
