# services/dashboard_service/routers/dashboard.py
from sqlalchemy.orm import Session
from fastapi import Request, Depends, APIRouter, HTTPException
from services.dashboard_service.schemas.dashboard import DashboardOut, Sale, Review, Discount, Recommendation
from services.dashboard_service.utils.fetch_data import get_sales_count, get_reviews_count
from common.config.settings import settings
from common.db.session import get_db
from common.models.dashboard_log import DashboardLog
from typing import List
import httpx

router = APIRouter()

AUTH_SERVICE_URL = settings.AUTH_SERVICE_URL
SALES_SERVICE_URL = settings.SALES_SERVICE_URL
REVIEW_SERVICE_URL = settings.REVIEW_SERVICE_URL
DISCOUNT_SERVICE_URL = settings.DISCOUNT_SERVICE_URL

def save_dashboard_log(db: Session, user_id: int, user_agent: str, notes: str = "Dashboard opened"):
    db_log = DashboardLog(user_id=user_id, user_agent=user_agent, notes=notes)
    db.add(db_log)
    db.commit()


@router.get("/all/users", response_model=List[dict])
async def get_all_users():
    try:
        async with httpx.AsyncClient() as client:
            url = f"{AUTH_SERVICE_URL}/auth/users"
            print(f"🔍 URL: {url}")
            resp = await client.get(url)
            print(f"📦 RESPONSE STATUS: {resp.status_code}")
            resp.raise_for_status()
            return resp.json()
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Помилка при отриманні користувачів: {str(e)}")

@router.get("/all/sales", response_model=List[Sale], operation_id="get_all_sales_dashboard")
async def get_all_sales():
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{SALES_SERVICE_URL}/sales/sales/")
            resp.raise_for_status()
            return resp.json()

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Помилка при отриманні продажів: {str(e)}")

@router.get("/all/reviews", response_model=List[Review])
async def get_all_reviews():
    try:
        async with httpx.AsyncClient() as client:
            # ✅ Исправленный путь
            resp = await client.get(f"{REVIEW_SERVICE_URL}/reviews/reviews/")
            resp.raise_for_status()
            return resp.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Помилка при отриманні відгуків: {str(e)}")

@router.get("/all/discounts", response_model=List[Discount])
async def get_all_discounts():
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{DISCOUNT_SERVICE_URL}/discounts/")
            resp.raise_for_status()
            return resp.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Помилка при отриманні знижок: {str(e)}")


@router.get("/all/recommendations", response_model=List[Recommendation])
async def get_all_recommendations():
    try:
        async with httpx.AsyncClient() as client:
            # ✅ Проверенный и скорректированный путь
            resp = await client.get(f"{REVIEW_SERVICE_URL}/reviews/recommendations/")
            resp.raise_for_status()
            return resp.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Помилка при отриманні рекомендацій: {str(e)}")

@router.get("/stats")
def get_dashboard_stats():
    return {"status": "ok"}

@router.get("/{user_id}", response_model=DashboardOut)
async def get_dashboard(user_id: int, request: Request, db: Session = Depends(get_db)):
    save_dashboard_log(db, user_id, request.headers.get("user-agent"))
    try:
        async with httpx.AsyncClient() as client:
            user_resp = await client.get(f"{AUTH_SERVICE_URL}/auth/users/{user_id}")
            user_resp.raise_for_status()

        user = user_resp.json()
        sales_count = await get_sales_count(user_id)
        reviews_count = await get_reviews_count(user_id)

        return DashboardOut(
            id=user["id"],
            full_name=user.get("full_name"),
            email=user.get("email") or user["login"],
            phone=user.get("phone"),
            avatar_url=user.get("avatar_url"),
            language=user.get("language"),
            bonus_balance=user.get("bonus_balance", 0),
            delivery_address=user.get("delivery_address"),
            sales_count=sales_count,
            reviews_count=reviews_count,
            discounts_count=0
        )
    except httpx.HTTPStatusError:
        raise HTTPException(status_code=404, detail="Користувача не знайдено")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Невідома помилка: {str(e)}")

