# ✅ services/review_service/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text

from common.db.base import Base
from common.db.session import engine, get_db
from services.review_service.api.routes import router
from services.review_service.models import review, recommendation  # 👈 нужны для создания таблиц

app = FastAPI(title="Review Service")

# 🔓 Разрешённые домены
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

# 🛠️ Создание таблиц при старте
@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    db_gen = get_db()
    db = next(db_gen)
    try:
        db.execute(text("SELECT 1"))
        print("✅ PostgreSQL подключение успешно (Review Service)")
    except Exception as e:
        print(f"❌ Ошибка подключения к PostgreSQL: {e}")
    finally:
        db.close()

# 🔗 Роуты
app.include_router(router, prefix="/reviews", tags=["Reviews"])

# 🌐 Корень
@app.get("/")
def root():
    return {"message": "Review Service is running"}


# uvicorn services.review_service.main:app --reload --port 8002