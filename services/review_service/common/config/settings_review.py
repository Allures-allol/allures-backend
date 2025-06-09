from pydantic_settings import BaseSettings
from pathlib import Path

class ReviewSettings(BaseSettings):
<<<<<<< HEAD
    ALLURES_DB_URL: str #Change to LOCAL_DB_URL after
=======
    # LOCAL_DB_URL: str
    MAINDB_URL: str  # Change to LOCAL_DB_URL after
>>>>>>> f8c40c6 (🚀 Update for test-heroku: cleanup GraphQL, add payment/discount features)

    class Config:
        env_file = Path(__file__).resolve().parents[4] / ".env.review"

settings_review = ReviewSettings()
