# ✅ services/review_service/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from services.review_service.db.database import init_db
from services.review_service.api.routes import router
#import nltk

# 📦 Загрузка NLTK ресурсов
#nltk.download('punkt')
#nltk.download('wordnet')

# 🚀 Инициализация FastAPI
app = FastAPI(title="Review Service")

# 🔓 CORS — разрешенные источники
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
    init_db()

# 🔗 Подключение маршрутов
app.include_router(router, prefix="/reviews", tags=["Reviews"])

# 🌐 Корневой маршрут
@app.get("/")
def root():
    return {"message": "Review Service is running"}
