# services/product_service/api/review_client.py

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
    created_at: Optional[str] = None

class RecommendationOut(BaseModel):
    id: int
    user_id: int
    product_id: int
    score: float

class ReviewsClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        self._client = httpx.Client(timeout=5.0)

    def get_reviews_by_product(self, product_id: int) -> List[ReviewOut]:
        url = f"{self.base_url}/reviews/product/{product_id}"
        try:
            r = self._client.get(url)
            r.raise_for_status()
            return [ReviewOut(**x) for x in r.json()]
        except httpx.RequestError:
            return []
        except httpx.HTTPStatusError:
            raise

    def get_user_recommendations(self, user_id: int) -> List[RecommendationOut]:
        url = f"{self.base_url}/reviews/recommendations/user/{user_id}"
        try:
            r = self._client.get(url)
            r.raise_for_status()
            return [RecommendationOut(**x) for x in r.json()]
        except httpx.RequestError:
            return []

reviews_client = ReviewsClient(settings.REVIEW_SERVICE_URL or "http://127.0.0.1:8002")
