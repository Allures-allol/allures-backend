# common/config/settings.py
from __future__ import annotations

import os
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Универсальные настройки для любого сервиса.
    Приоритет подключения к БД:
      1) DATABASE_URL (пер-сервис)
      2) MAINDB_URL   (общая, как у тебя сейчас)
    """

    # Подключение к БД
    DATABASE_URL: str = Field(default="", alias="DATABASE_URL")
    MAINDB_URL: str = Field(default="", alias="MAINDB_URL")

    # Отладочные флаги
    DB_ECHO: bool = Field(default=False, alias="DB_ECHO")  # echo SQL в лог

    # URL других сервисов (дефолты — внутренняя docker-сеть)
    AUTH_SERVICE_URL: str = Field(default="http://auth_service:8000", alias="AUTH_SERVICE_URL")
    PRODUCT_SERVICE_URL: str = Field(default="http://product_service:8000", alias="PRODUCT_SERVICE_URL")
    REVIEW_SERVICE_URL: str = Field(default="http://review_service:8000", alias="REVIEW_SERVICE_URL")
    PAYMENTS_SERVICE_URL: str = Field(default="http://payment_service:8000", alias="PAYMENTS_SERVICE_URL")
    PROFILE_SERVICE_URL: str = Field(default="http://profile_service:8000", alias="PROFILE_SERVICE_URL")
    DISCOUNT_SERVICE_URL: str = Field(default="http://discount_service:8000", alias="DISCOUNT_SERVICE_URL")
    ADMIN_SERVICE_URL: str = Field(default="http://admin_service:8000", alias="ADMIN_SERVICE_URL")
    SUBSCRIPTION_SERVICE_URL: str = Field(default="http://subscription_service:8000", alias="SUBSCRIPTION_SERVICE_URL")
    # TODO: включить DASHBOARD_SERVICE_URL после запуска dashboard_service
    # DASHBOARD_SERVICE_URL: str = Field(default="http://dashboard_service:8000", alias="DASHBOARD_SERVICE_URL")

    # Прочее (делай alias под свои ключи)
    NOWPAYMENTS_API_KEY: str | None = Field(default=None, alias="NOWPAYMENTS_API_KEY")
    NGROK_WEBHOOK_URL: str | None = Field(default=None, alias="NGROK_WEBHOOK_URL")

    model_config = SettingsConfigDict(
        env_file=os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.env")),
        env_file_encoding="utf-8",
        extra="allow",
        case_sensitive=True,
    )

    @property
    def effective_db_url(self) -> str:
        """
        Главная точка входа для session.py:
        сначала берём DATABASE_URL (пер‑сервис),
        если пусто — падаем на MAINDB_URL (как у тебя сейчас).
        """
        return self.DATABASE_URL or self.MAINDB_URL


settings = Settings()
