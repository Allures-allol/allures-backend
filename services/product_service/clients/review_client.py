# services/product_service/clients/review_client.py
from typing import List, Optional
import httpx
from pydantic import BaseModel
from common.config.settings import settings


class ReviewOut(BaseModel):
    id: int
    product_id: int
    user_id: int
    text: str
    sentiment: Optional[str] = None
    pos_score: Optional[float] = None
    neg_score: Optional[float] = None
    created_at: Optional[str] = None


class RecommendationOut(BaseModel):
    id: int
    user_id: int
    product_id: int
    score: float


def _build_base() -> str:
    """
    Единственный источник BASE. Для DEV: http://127.0.0.1:8002
    Для PROD: https://api.alluresallol.com/review
    """
    base = getattr(settings, "REVIEW_SERVICE_BASE", None) or "http://127.0.0.1:8002"
    return base.rstrip("/")


class ReviewsClient:
    def __init__(self, base_url: Optional[str] = None, timeout: float = 5.0):
        base = (base_url or _build_base()).rstrip("/")
        # print(f"[reviews_client] BASE = {base}")  # опционально
        self.base_url = base
        self._client = httpx.Client(timeout=timeout)

    def get_base(self) -> str:
        return self.base_url

    def get_reviews_by_product(self, product_id: int) -> List[ReviewOut]:
        url = f"{self.base_url}/reviews/product/{product_id}"
        r = self._client.get(url)
        r.raise_for_status()
        return [ReviewOut(**x) for x in r.json()]

    def get_user_recommendations(self, user_id: int) -> List[RecommendationOut]:
        url = f"{self.base_url}/recommendations/user/{user_id}"
        r = self._client.get(url)
        r.raise_for_status()
        return [RecommendationOut(**x) for x in r.json()]

    def close(self) -> None:
        try:
            self._client.close()
        except Exception:
            pass


reviews_client = ReviewsClient()

