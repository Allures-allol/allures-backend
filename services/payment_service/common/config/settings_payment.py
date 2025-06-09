
from pydantic import BaseSettings

class Settings(BaseSettings):
    NGROK_WEBHOOK_URL: str = ""

settings = Settings()
