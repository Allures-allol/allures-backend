# services/payment_service/settings_payment.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    NOWPAYMENTS_API_KEY: str
    NGROK_WEBHOOK_URL: str = ""
    MAINDB_URL: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings_payment = Settings()


