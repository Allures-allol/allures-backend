from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from common.db.session import get_db

from services.product_service.api.routes import router as product_router
from services.review_service.api.routes import router as review_router

load_dotenv()

app = FastAPI(title="Allures Backend")

app.include_router(product_router, prefix="/products", tags=["products"])
app.include_router(review_router, prefix="/reviews", tags=["reviews"])

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    db_gen = get_db()
    db = next(db_gen)
    try:
        db.execute("SELECT 1")
        print("✅ MSSQL подключение успешно (AlluresDb)")
    except Exception as e:
        print(f"❌ Ошибка подключения к MSSQL: {e}")
    finally:
        db.close()

@app.get("/")
def root():
    return {"message": "Hello from Allures Backend"}