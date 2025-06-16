# common/config/settings.py
import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    NOWPAYMENTS_API_KEY: str = ""
    NGROK_WEBHOOK_URL: str = ""
    MAINDB_URL: str

    PRODUCT_SERVICE_URL: str = "http://product_service:8000"
    SALES_SERVICE_URL: str = "http://sales_service:8001"
    REVIEW_SERVICE_URL: str = "http://review_service:8002"
    AUTH_SERVICE_URL: str = "http://auth_service:8003"
    PROFILE_SERVICE_URL: str = "http://profile_service:8004"
    PAYMENTS_SERVICE_URL: str = "http://payment_service:8005"
    DISCOUNT_SERVICE_URL: str = "http://discount_service:8006"
    DASHBOARD_SERVICE_URL: str = "http://dashboard_service:8007"

    model_config = SettingsConfigDict(
        env_file=".env" if os.getenv("USE_DOTENV", "true").lower() == "true" else None,
        env_file_encoding="utf-8",
        extra="allow"
    )

settings = Settings()
