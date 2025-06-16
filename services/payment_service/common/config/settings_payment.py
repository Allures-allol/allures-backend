# services/payment_service/settings_payment.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    MAINDB_URL: str
    SA_PASSWORD: str
    PRODUCT_SERVICE_URL: str
    SALES_SERVICE_URL: str
    REVIEW_SERVICE_URL: str
    AUTH_SERVICE_URL: str
    PROFILE_SERVICE_URL: str
    PAYMENTS_SERVICE_URL: str
    DISCOUNT_SERVICE_URL: str
    DASHBOARD_SERVICE_URL: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "allow"  # ✅ если хочешь не указывать всё вручную

settings_payment = Settings()


