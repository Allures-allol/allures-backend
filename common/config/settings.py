# common/config/settings.py
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
import os

class Settings(BaseSettings):
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str

    # 🔐 API ключи
    NOWPAYMENTS_API_KEY: str = Field(..., alias="NOWPAYMENTS_API_KEY")
    NGROK_WEBHOOK_URL: str = Field(..., alias="NGROK_WEBHOOK_URL")

    # 💾 База данных
    MAINDB_URL: str = Field(..., alias="MAINDB_URL")

    # 🌐 Ссылки на микросервисы
    PRODUCT_SERVICE_URL: str = Field(..., alias="PRODUCT_SERVICE_URL")
    SALES_SERVICE_URL: str = Field(..., alias="SALES_SERVICE_URL")
    REVIEW_SERVICE_URL: str = Field(..., alias="REVIEW_SERVICE_URL")
    AUTH_SERVICE_URL: str = Field(..., alias="AUTH_SERVICE_URL")
    PROFILE_SERVICE_URL: str = Field(..., alias="PROFILE_SERVICE_URL")
    PAYMENTS_SERVICE_URL: str = Field(..., alias="PAYMENTS_SERVICE_URL")
    DISCOUNT_SERVICE_URL: str = Field(..., alias="DISCOUNT_SERVICE_URL")
    DASHBOARD_SERVICE_URL: str = Field(..., alias="DASHBOARD_SERVICE_URL")

    model_config = SettingsConfigDict(
        env_file=os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.env")),
        env_file_encoding="utf-8",
        extra="allow"
    )


settings = Settings()