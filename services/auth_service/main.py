# services/auth_service/main.py
import sys, os
from dotenv import load_dotenv
load_dotenv()

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from common.db.session import get_db

from services.auth_service.routers import auth as auth_router
from services.auth_service.routers import profile as profile_router
from services.auth_service.routers import user as user_router

jwt_secret = os.getenv("JWT_SECRET")
print(f" JWT_SECRET загружен: {jwt_secret[:10]}... (длина = {len(jwt_secret)})" if jwt_secret else "❌ JWT_SECRET НЕ НАЙДЕН!")

_use_root = os.getenv("AUTH_USE_ROOT_PATH", "0").strip().lower() in ("1", "true", "yes")
ROOT_PATH = "/auth" if _use_root else ""

app = FastAPI(
    title="Auth Service",
    root_path="/auth",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# НЕ трогаем app.openapi() / app.openapi_schema — FastAPI сам всё соберёт из Security

_cors_env = os.getenv("CORS_ALLOWED_ORIGINS", "")
ALLOWED_ORIGINS = [o.strip() for o in _cors_env.split(",") if o.strip()] if _cors_env.strip() else [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://alluresallol.com",
    "https://api.alluresallol.com",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# роутеры
app.include_router(auth_router.router)
app.include_router(profile_router.router)
app.include_router(user_router.router)

print(f"✅ ALLOWED_ORIGINS: {ALLOWED_ORIGINS}")

@app.get("/health", tags=["meta"])
def health():
    return {"status": "ok"}

@app.on_event("startup")
def startup_event():
    db_gen = get_db(); db = next(db_gen)
    try:
        db.execute(text("SELECT 1"))
        print(" PostgreSQL подключение успешно (Auth Service)")
    except Exception as e:
        print(f" Ошибка подключения к PostgreSQL: {e}")
    finally:
        db.close()

@app.get("/", tags=["meta"])
def read_root():
    return {"message": "Authorization Service is running. Pipeline test"}

@app.get("/__debug/db_url")
def dbg_db():
    return {"MAINDB_URL": os.getenv("MAINDB_URL")}

# uvicorn services.auth_service.main:app --reload --port 8003