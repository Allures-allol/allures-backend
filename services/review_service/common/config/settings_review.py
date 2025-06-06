from pydantic_settings import BaseSettings
from pathlib import Path

class ReviewSettings(BaseSettings):
    ALLURES_DB_URL: str #Change to LOCAL_DB_URL after

    class Config:
        env_file = Path(__file__).resolve().parents[4] / ".env.review"

settings_review = ReviewSettings()


