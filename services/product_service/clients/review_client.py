# services/product_service/clients/review_client.py
from typing import List, Optional, Dict, Any
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
    REVIEW_SERVICE_URL — обязательная часть (по умолчанию http://127.0.0.1:8002)
    REVIEW_BASE_PATH   — опциональный префикс (по умолчанию '/review')
    Примеры:
      URL=http://127.0.0.1:8002, BASE_PATH=/review  -> http://127.0.0.1:8002/review
      URL=http://127.0.0.1:8002, BASE_PATH=        -> http://127.0.0.1:8002
    """
    origin = (getattr(settings, "REVIEW_SERVICE_URL", None) or "http://127.0.0.1:8002").rstrip("/")
    base_path = getattr(settings, "REVIEW_BASE_PATH", "/review")
    base_path = "" if base_path is None else str(base_path).strip()
    if base_path in ("", "/"):
        return origin
    return origin + "/" + base_path.lstrip("/")


class ReviewsClient:
    def __init__(self, base_url: Optional[str] = None, timeout: float = 20.0):
        base = (base_url or _build_base()).rstrip("/")
        self.base_url = base
        self._client = httpx.Client(timeout=timeout)

    def get_base(self) -> str:
        return self.base_url

    def get_reviews_by_product(self, product_id: int) -> List[ReviewOut]:
        url = f"{self.base_url}/product/{product_id}"
        r = self._client.get(url)
        r.raise_for_status()
        return [ReviewOut(**x) for x in r.json()]

    def get_user_recommendations(self, user_id: int) -> List[RecommendationOut]:
        url = f"{self.base_url}/recommendations/user/{user_id}"
        r = self._client.get(url)
        r.raise_for_status()
        return [RecommendationOut(**x) for x in r.json()]

    def probe(self) -> Dict[str, Any]:
        results: Dict[str, Any] = {}
        for path in ["/", "/product/1", "/recommendations/user/1"]:
            url = f"{self.base_url}{path}"
            try:
                r = self._client.get(url)
                results[path] = {"code": r.status_code}
            except httpx.HTTPError as e:
                results[path] = {"error": f"transport error: {e}"}
        return {"base": self.base_url, "results": results}

    def close(self) -> None:
        try:
            self._client.close()
        except Exception:
            pass

 # --- : deletes ---
    def delete_review(self, review_id: int) -> None:
        url = f"{self.base_url}/reviews/{review_id}"
        r = self._client.delete(url)
        r.raise_for_status()
        return None

    def delete_reviews_of_product(self, product_id: int, user_id: Optional[int] = None) -> dict:
        url = f"{self.base_url}/product/{product_id}"
        params = {}
        if user_id is not None:
            params["user_id"] = user_id
        r = self._client.delete(url, params=params)
        r.raise_for_status()
        return r.json()  # {"deleted": N}

    def delete_recommendation(self, rec_id: int) -> None:
        url = f"{self.base_url}/recommendations/{rec_id}"
        r = self._client.delete(url)
        r.raise_for_status()
        return None

    def delete_recommendations_of_user(self, user_id: int) -> dict:
        url = f"{self.base_url}/recommendations/user/{user_id}"
        r = self._client.delete(url)
        r.raise_for_status()
        return r.json()  # {"deleted": N}

reviews_client = ReviewsClient()
