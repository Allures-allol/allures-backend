# services/payment_service/settings_payment.py
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    NOWPAYMENTS_API_KEY: str = Field(..., alias="NOWPAYMENTS_API_KEY")
    NGROK_WEBHOOK_URL: str = Field(..., alias="NGROK_WEBHOOK_URL")

    MAINDB_URL: str = Field(..., alias="MAINDB_URL")

    # Добавь нужные только для payment_service или скопируй все
    AUTH_SERVICE_URL: str = Field(..., alias="AUTH_SERVICE_URL")
    SALES_SERVICE_URL: str = Field(..., alias="SALES_SERVICE_URL")
    REVIEW_SERVICE_URL: str = Field(..., alias="REVIEW_SERVICE_URL")
    DISCOUNT_SERVICE_URL: str = Field(..., alias="DISCOUNT_SERVICE_URL")
    PAYMENTS_SERVICE_URL: str = Field(..., alias="PAYMENTS_SERVICE_URL")
    PRODUCT_SERVICE_URL: str = Field(..., alias="PRODUCT_SERVICE_URL")
    PROFILE_SERVICE_URL: str = Field(..., alias="PROFILE_SERVICE_URL")
    DASHBOARD_SERVICE_URL: str = Field(..., alias="DASHBOARD_SERVICE_URL")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="forbid"
    )

settings_payment = Settings()