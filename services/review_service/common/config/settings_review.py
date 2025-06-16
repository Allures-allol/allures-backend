# services/review_service/common/config/settings_review.py
from pydantic_settings import BaseSettings
from pathlib import Path

class ReviewSettings(BaseSettings):
    MAINDB_URL: str

    REVIEW_SERVICE_URL: str = "http://review_service:8002"

    class Config:
        env_file = Path(__file__).resolve().parents[4] / ".env"
        extra = "allow"
        #env_file = Path(__file__).resolve().parents[4] / ".env.review"

settings_review = ReviewSettings()
