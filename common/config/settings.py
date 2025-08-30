# common/config/settings.py
from __future__ import annotations
import os
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Prod: одна общая БД (MAINDB_URL).
    Формат для SQLAlchemy с psycopg2: postgresql+psycopg2://... ?sslmode=require
    """
    MAINDB_URL: str = Field(default="", alias="MAINDB_URL")
    DB_ECHO: bool = Field(default=False, alias="DB_ECHO")

    AUTH_SERVICE_URL: str = Field(default="http://auth_service:8000", alias="AUTH_SERVICE_URL")
    PRODUCT_SERVICE_URL: str = Field(default="http://product_service:8000", alias="PRODUCT_SERVICE_URL")
    REVIEW_SERVICE_URL: str = Field(default="http://review_service:8000", alias="REVIEW_SERVICE_URL")
    PROFILE_SERVICE_URL: str = Field(default="http://profile_service:8000", alias="PROFILE_SERVICE_URL")
    DISCOUNT_SERVICE_URL: str = Field(default="http://discount_service:8000", alias="DISCOUNT_SERVICE_URL")
    ADMIN_SERVICE_URL: str = Field(default="http://admin_service:8000", alias="ADMIN_SERVICE_URL")
    SUBSCRIPTION_SERVICE_URL: str = Field(default="http://subscription_service:8000", alias="SUBSCRIPTION_SERVICE_URL")
    # DASHBOARD_SERVICE_URL: str = Field(default="http://dashboard_service:8000", alias="DASHBOARD_SERVICE_URL")

    # ЕДИНОЕ имя переменной для платёжного сервиса
    PAYMENT_SERVICE_URL: str | None = Field(default=None, alias="PAYMENT_SERVICE_URL")

    # NowPayments
    NOWPAYMENTS_API_KEY: str | None = Field(default=None, alias="NOWPAYMENTS_API_KEY")
    NGROK_WEBHOOK_URL: str | None = Field(default=None, alias="NGROK_WEBHOOK_URL")

    # Monobank
    MONOBANK_TOKEN: str | None = Field(default=None, alias="MONOBANK_TOKEN")
    MONOBANK_WEBHOOK_SECRET: str | None = Field(default=None, alias="MONOBANK_WEBHOOK_SECRET")  # если отличается от токена
    MONOBANK_REDIRECT_URL: str = Field(default="https://example.com/return", alias="MONOBANK_REDIRECT_URL")
    MONOBANK_WEBHOOK_URL: str | None = Field(default=None, alias="MONOBANK_WEBHOOK_URL")  # если не задан — возьмём из PAYMENT_SERVICE_URL

    model_config = SettingsConfigDict(
        env_file=os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.env")),
        env_file_encoding="utf-8",
        extra="allow",
        case_sensitive=True,
    )

    @property
    def effective_db_url(self) -> str:
        return self.MAINDB_URL

settings = Settings()
