import httpx
from common.config.settings import settings

SALES_SERVICE_URL = settings.SALES_SERVICE_URL
REVIEW_SERVICE_URL = settings.REVIEW_SERVICE_URL


async def get_sales_count(user_id: int) -> int:
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(f"{SALES_SERVICE_URL}/sales/user/{user_id}")
            if resp.status_code == 200:
                return len(resp.json())
        except Exception as e:
            print("Ошибка при получении продаж:", e)
    return 0


async def get_reviews_count(user_id: int) -> int:
    async with httpx.AsyncClient() as client:
        try:
            # ✅ Исправленный путь
            resp = await client.get(f"{REVIEW_SERVICE_URL}/reviews/reviews/")
            if resp.status_code == 200:
                reviews = resp.json()
                return len([r for r in reviews if r["user_id"] == user_id])
        except Exception as e:
            print("Ошибка при получении отзывов:", e)
    return 0
