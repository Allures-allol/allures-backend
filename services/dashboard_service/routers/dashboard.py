# services/dashboard_service/routers/dashboard.py
from sqlalchemy.orm import Session
from fastapi import APIRouter, Request, Depends, APIRouter, HTTPException, Query, Path
from services.dashboard_service.schemas.dashboard import DashboardOut, DashboardLogOut, Sale, Review, Discount, Recommendation
from services.dashboard_service.utils.fetch_data import get_sales_count, get_reviews_count
from common.config.settings import settings
from common.db.session import get_db
from datetime import datetime
from common.models.dashboard_log import DashboardLog
from common.models.subscriptions import Subscription, UserSubscription
from common.models.payment import Payment
from services.dashboard_service.schemas.dashboard import UserProfileUpdate

from typing import List, Optional
import httpx

router = APIRouter()

AUTH_SERVICE_URL = settings.AUTH_SERVICE_URL
SALES_SERVICE_URL = settings.SALES_SERVICE_URL
REVIEW_SERVICE_URL = settings.REVIEW_SERVICE_URL
DISCOUNT_SERVICE_URL = settings.DISCOUNT_SERVICE_URL

# Функция логирования входа в дашборд
def save_dashboard_log(db: Session, user_id: int, user_agent: str, notes: str = "Вхід у кабінет"):
    try:
        log = DashboardLog(
            user_id=user_id,
            user_agent=user_agent,
            notes=notes
        )
        db.add(log)
        db.commit()
    except Exception as e:
        db.rollback()
        print(f" Error saving dashboard log: {str(e)}")


@router.get("/logs/", response_model=List[DashboardLogOut])
def get_logs(
    db: Session = Depends(get_db),
    user_id: Optional[int] = Query(None, description="Фильтр по ID пользователя"),
    from_date: Optional[datetime] = Query(None, description="Начальная дата"),
    to_date: Optional[datetime] = Query(None, description="Конечная дата"),
    sort_desc: bool = Query(True, description="Сортировать по убыванию времени")
):
    query = db.query(DashboardLog)

    # Фильтры
    if user_id is not None:
        query = query.filter(DashboardLog.user_id == user_id)
    if from_date is not None:
        query = query.filter(DashboardLog.fetched_at >= from_date)
    if to_date is not None:
        query = query.filter(DashboardLog.fetched_at <= to_date)

    # Сортировка
    if sort_desc:
        query = query.order_by(DashboardLog.fetched_at.desc())
    else:
        query = query.order_by(DashboardLog.fetched_at.asc())

    return query.all()


# Получение всех пользователей
@router.get("/all/users", response_model=List[dict])
async def get_all_users():
    try:
        async with httpx.AsyncClient() as client:
            url = f"{AUTH_SERVICE_URL}/auth/users"
            resp = await client.get(url)
            resp.raise_for_status()
            return resp.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Помилка при отриманні користувачів: {str(e)}")

# Получение всех продаж
@router.get("/all/sales", response_model=List[Sale])
async def get_all_sales():
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{SALES_SERVICE_URL}/sales/sales/")
            resp.raise_for_status()
            return resp.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Помилка при отриманні продажів: {str(e)}")

# Получение всех отзывов
@router.get("/all/reviews", response_model=List[Review])
async def get_all_reviews():
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{REVIEW_SERVICE_URL}/reviews/reviews/")
            resp.raise_for_status()
            return resp.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Помилка при отриманні відгуків: {str(e)}")

# Получение всех скидок
@router.get("/all/discounts", response_model=List[Discount])
async def get_all_discounts():
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{DISCOUNT_SERVICE_URL}/discounts/")
            resp.raise_for_status()
            return resp.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Помилка при отриманні знижок: {str(e)}")

# Получение всех рекомендаций
@router.get("/all/recommendations", response_model=List[Recommendation])
async def get_all_recommendations():
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{REVIEW_SERVICE_URL}/reviews/recommendations/")
            resp.raise_for_status()
            return resp.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Помилка при отриманні рекомендацій: {str(e)}")

@router.get("/profile/{user_id}", summary="Отримати профіль користувача", response_model=DashboardOut)
async def get_user_profile(user_id: int):
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

# эндпоинт для теста
@router.get("/stats")
def get_dashboard_stats():
    return {"status": "ok"}

# Основной эндпоинт дашборда (логирует вход и возвращает агрегированные данные)
@router.get("/{user_id}", response_model=DashboardOut)
async def get_dashboard(user_id: int, request: Request, db: Session = Depends(get_db)):
    user_agent = request.headers.get("user-agent", "unknown")
    save_dashboard_log(db, user_id=user_id, user_agent=user_agent)

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


