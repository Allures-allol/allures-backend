#services/dashboard_service/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from services.dashboard_service.routers import dashboard
from common.config.settings import settings
from common.db.session import get_db

app = FastAPI(title="Dashboard Service")

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

# 🔗 Роутер
app.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])

# ✅ Проверка подключения к PostgreSQL
@app.on_event("startup")
def startup_event():
    db_gen = get_db()
    db = next(db_gen)
    try:
        db.execute(text("SELECT 1"))
        print("✅ PostgreSQL подключение успешно (Dashboard Service)")
    except Exception as e:
        print(f"❌ Ошибка подключения к PostgreSQL: {e}")
    finally:
        db.close()

# 🌐 Корень
@app.get("/")
def root():
    return {"message": "Dashboard Service is running"}


# uvicorn services.dashboard_service.main:app --reload --port 8007
