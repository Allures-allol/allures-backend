# services/product_service/clients/review_client.py
from typing import List, Optional
from pydantic import BaseModel
import httpx
from common.config.settings import settings

class ReviewOut(BaseModel):
    id: int
    product_id: int
    user_id: int
    text: str
    sentiment: Optional[str] = None
    pos_score: Optional[float] = None
    neg_score: Optional[float] = None
    # можно и datetime, если хочешь строже типизировать
    created_at: Optional[str] = None

class RecommendationOut(BaseModel):
    id: int
    user_id: int
    product_id: int
    score: float

def _build_base() -> str:
    """
    Склеиваем ORIGIN и ROOT:
      PROD: ORIGIN=https://api.alluresallol.com, ROOT=/review  -> https://api.alluresallol.com/review
      LOCAL: ORIGIN=http://127.0.0.1:8002, ROOT=""             -> http://127.0.0.1:8002
    """
    origin = (getattr(settings, "REVIEW_SERVICE_ORIGIN", None) or
              getattr(settings, "REVIEW_SERVICE_URL", None) or
              "http://127.0.0.1:8002").rstrip("/")
    root = getattr(settings, "REVIEW_SERVICE_ROOT", "") or ""
    root = ("/" + root.strip("/")) if root else ""
    return origin + root  # без завершающего /

class ReviewsClient:
    def __init__(self, base: Optional[str] = None, timeout: float = 5.0):
        self.base = base or _build_base()           # напр. https://api.alluresallol.com/review
        self._client = httpx.Client(timeout=timeout)

    def get_reviews_by_product(self, product_id: int) -> List[ReviewOut]:
        # Роут в Review-сервисе: include_router(..., prefix="/reviews")
        # и эндпоинт: @router.get("/product/{product_id}")
        url = f"{self.base}/reviews/product/{product_id}"
        r = self._client.get(url)
        r.raise_for_status()
        return [ReviewOut(**x) for x in r.json()]

    def get_user_recommendations(self, user_id: int) -> List[RecommendationOut]:
        url = f"{self.base}/reviews/recommendations/user/{user_id}"
        r = self._client.get(url)
        r.raise_for_status()
        return [RecommendationOut(**x) for x in r.json()]

# дефолтный клиент
reviews_client = ReviewsClient()

