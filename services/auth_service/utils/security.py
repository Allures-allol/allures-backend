# services/auth_service/utils/security.py
from passlib.context import CryptContext
# реэкспортируем общие JWT-утилиты, НЕ переопределяя их
from common.security.jwt import create_access_token, verify_access_token

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ---- Пароли ----
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

__all__ = [
    "hash_password", "verify_password",
    "create_access_token", "verify_access_token",
]
