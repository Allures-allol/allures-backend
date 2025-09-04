# common/config/settings.py
from __future__ import annotations
import os
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # --- DB ---
    DATABASE_URL: str | None = Field(default=None, alias="DATABASE_URL")
    MAINDB_URL: str | None = Field(default=None, alias="MAINDB_URL")

    # на случай, если передают по частям (часто так в Docker/Cloud)
    POSTGRES_USER: str | None = Field(default=None, alias="POSTGRES_USER")
    POSTGRES_PASSWORD: str | None = Field(default=None, alias="POSTGRES_PASSWORD")
    POSTGRES_DB: str | None = Field(default=None, alias="POSTGRES_DB")
    POSTGRES_HOST: str | None = Field(default=None, alias="POSTGRES_HOST")
    POSTGRES_PORT: str | None = Field(default="5432", alias="POSTGRES_PORT")

    DB_ECHO: bool = Field(default=False, alias="DB_ECHO")

    # --- services & payments (как у вас было) ---
    AUTH_SERVICE_URL: str = Field(default="http://auth_service:8000", alias="AUTH_SERVICE_URL")
    PRODUCT_SERVICE_URL: str = Field(default="http://product_service:8000", alias="PRODUCT_SERVICE_URL")
    REVIEW_SERVICE_URL: str = Field(default="http://review_service:8000", alias="REVIEW_SERVICE_URL")
    PROFILE_SERVICE_URL: str = Field(default="http://profile_service:8000", alias="PROFILE_SERVICE_URL")
    DISCOUNT_SERVICE_URL: str = Field(default="http://discount_service:8000", alias="DISCOUNT_SERVICE_URL")
    ADMIN_SERVICE_URL: str = Field(default="http://admin_service:8000", alias="ADMIN_SERVICE_URL")
    SUBSCRIPTION_SERVICE_URL: str = Field(default="http://subscription_service:8000", alias="SUBSCRIPTION_SERVICE_URL")

    PAYMENT_SERVICE_URL: str | None = Field(default=None, alias="PAYMENT_SERVICE_URL")

    NOWPAYMENTS_API_KEY: str | None = Field(default=None, alias="NOWPAYMENTS_API_KEY")
    NGROK_WEBHOOK_URL: str | None = Field(default=None, alias="NGROK_WEBHOOK_URL")

    MONOBANK_TOKEN: str | None = Field(default=None, alias="MONOBANK_TOKEN")
    MONOBANK_WEBHOOK_SECRET: str | None = Field(default=None, alias="MONOBANK_WEBHOOK_SECRET")
    MONOBANK_REDIRECT_URL: str = Field(default="https://example.com/return", alias="MONOBANK_REDIRECT_URL")
    MONOBANK_WEBHOOK_URL: str | None = Field(default=None, alias="MONOBANK_WEBHOOK_URL")

    model_config = SettingsConfigDict(
        env_file=os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.env")),
        env_file_encoding="utf-8",
        extra="allow",
        case_sensitive=True,
    )

    @property
    def effective_db_url(self) -> str:
        # 1) приоритет DATABASE_URL
        if self.DATABASE_URL:
            return self.DATABASE_URL
        # 2) затем MAINDB_URL
        if self.MAINDB_URL:
            return self.MAINDB_URL
        # 3) сборка из POSTGRES_*
        if self.POSTGRES_USER and self.POSTGRES_PASSWORD and self.POSTGRES_DB:
            host = self.POSTGRES_HOST or "localhost"
            port = self.POSTGRES_PORT or "5432"
            # универсальная схема без указания драйвера тоже ок
            return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{host}:{port}/{self.POSTGRES_DB}"
        return ""

settings = Settings()

