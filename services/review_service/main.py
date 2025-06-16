# ✅ services/review_service/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from common.db.base import Base
from services.review_service.api.routes import router
from services.review_service.db.database import engine  # нужен для bind в create_all
from services.review_service.models import review, recommendation  # 👈 обязательно, чтобы таблицы создались

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

# 🔗 Роуты
app.include_router(router, prefix="/reviews", tags=["Reviews"])

# 🌐 Корень
@app.get("/")
def root():
    return {"message": "Review Service is running"}

# uvicorn services.review_service.main:app --reload --port 8002