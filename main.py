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
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from common.db.session import get_db

from services.product_service.api.routes import router as product_router
from services.review_service.api.routes import router as review_router
from services.sales_service.api.routes import router as sales_router
from services.payment_service.routers.payment import router as payment_router
from services.discount_service.routers.discount import router as discount_router
from services.auth_service.routers.auth import router as auth_router

load_dotenv()

app = FastAPI(title="Allures Backend")
def root():
	pass
# Подключение всех роутеров
app.include_router(product_router, prefix="/products", tags=["products"])
app.include_router(review_router, prefix="/reviews", tags=["reviews"])
app.include_router(sales_router, prefix="/sales", tags=["sales"])
app.include_router(payment_router, prefix="/payment", tags=["payment"])
app.include_router(discount_router, prefix="/discounts", tags=["discounts"])
app.include_router(auth_router, prefix="/auth", tags=["auth"])

# CORS
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
        print("✅ PostgrSQL подключение успешно (AlluresDb)")
    except Exception as e:
        print(f"❌ Ошибка подключения к PostgreSQL: {e}")
    finally:
        db.close()

@app.get("/")
def root():
    return {"message": "Hello from Allures Backend"}
