#корень /main.py
import sys
import os
# Добавление корневого пути (для импорта модулей из /services и /common)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
#import common.utils.env_loader

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from common.db.session import get_db
from sqlalchemy import text
from common.db.base import Base
from common.db.session import engine
import common.models
from services.review_service.models.review import Review
from services.review_service.models.recommendation import Recommendation
from sqlalchemy.orm import Session
from common.db.session import SessionLocal

# Импорт роутеров всех микросервисов
from services.product_service.api.routes import router as product_router
from services.product_service.api import image_classifier_router
from services.review_service.api.routes import router as review_router
from services.sales_service.api.routes import router as sales_router
from services.payment_service.routers.payment import router as payment_router
from services.discount_service.routers.discount import router as discount_router
from services.auth_service.routers.auth import router as auth_router
from services.dashboard_service.routers.dashboard import router as dashboard_router
from services.admin_service.routers.admin_router import router as admin_router
from services.subscription_service.routers.subscription_routers import router as subscription_router
from services.review_service.models.review import Review
from bulk_classify_and_save import load_and_classify_bulk

# Загрузка переменных окружения
load_dotenv()

app = FastAPI(title="Allures Backend")

# Подключение всех роутеров
app.include_router(product_router, prefix="/products", tags=["Products"])
app.include_router(image_classifier_router.router, prefix="/product", tags=["AI classifier"])
app.include_router(review_router, prefix="/reviews", tags=["Reviews"])
app.include_router(sales_router, prefix="/sales", tags=["Sales"])
app.include_router(payment_router, prefix="/payment", tags=["Payment"])
app.include_router(discount_router, prefix="/discounts", tags=["Discounts"])
app.include_router(auth_router, prefix="/auth", tags=["Auth"])
# app.include_router(dashboard_router, prefix="/dashboard", tags=["Dashboard"])
app.include_router(admin_router, prefix="/admin", tags=["Admin"])
app.include_router(subscription_router, prefix="/subscription", tags=["Subscription"])

# Разрешения CORS
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

# db_url = os.getenv("MAINDB_URL")
# print(" MAINDB_URL:", db_url)

# Проверка подключения к БД
@app.on_event("startup")
def startup_event():
    from sqlalchemy import text
    from common.db.base import Base
    from common.db.session import engine

    db_gen = get_db()
    db = next(db_gen)
    try:
        db.execute(text("SELECT 1"))
        print(" PostgreSQL подключение успешно (Allures Backend)")

        # Создание таблиц
        Base.metadata.create_all(bind=engine)
        print(" Таблицы успешно созданы (если не существовали)")

    except Exception as e:
        print(f" Ошибка подключения к PostgreSQL: {e}")
    finally:
        db.close()

@app.get("/")
def root():
    return {"message": "Allures Backend"}

def main():
    db: Session = SessionLocal()
    load_and_classify_bulk(db)

if __name__ == "__main__":
    main()

# uvicorn main:app --reload --port 8008