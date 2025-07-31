# services/review_service/common/config/settings_review.py
from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
import os


class ReviewSettings(BaseSettings):
    
    # API ключи
    NOWPAYMENTS_API_KEY: str = Field(..., alias="NOWPAYMENTS_API_KEY")
    NGROK_WEBHOOK_URL: str = Field(..., alias="NGROK_WEBHOOK_URL")

    # База данных
    MAINDB_URL: str = Field(..., alias="MAINDB_URL")

    # Ссылки на микросервисы
    PRODUCT_SERVICE_URL: str = Field(..., alias="PRODUCT_SERVICE_URL")
    SALES_SERVICE_URL: str = Field(..., alias="SALES_SERVICE_URL")
    REVIEW_SERVICE_URL: str = Field(..., alias="REVIEW_SERVICE_URL")
    AUTH_SERVICE_URL: str = Field(..., alias="AUTH_SERVICE_URL")
    PROFILE_SERVICE_URL: str = Field(..., alias="PROFILE_SERVICE_URL")
    PAYMENTS_SERVICE_URL: str = Field(..., alias="PAYMENTS_SERVICE_URL")
    DISCOUNT_SERVICE_URL: str = Field(..., alias="DISCOUNT_SERVICE_URL")
    # DASHBOARD_SERVICE_URL: str = Field(..., alias="DASHBOARD_SERVICE_URL")
    ADMIN_SERVICE_URL: str = Field(..., alias="ADMIN_SERVICE_URL")
    SUBSCRIPTION_SERVICE_URL: str = Field(..., alias="SUBSCRIPTION_SERVICE_URL")

    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parents[4] / ".env",  #  Автоматически ищет .env в корне проекта
        env_file_encoding="utf-8",
        extra="allow",
        case_sensitive=True
    )

settings_review = ReviewSettings()

if __name__ == "__main__":
    print("✅ MAINDB_URL:", settings_review.MAINDB_URL)
