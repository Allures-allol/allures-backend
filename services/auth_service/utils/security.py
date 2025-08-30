# services/auth_service/utils/security.py
import os, time, secrets
from typing import Dict, Any
from passlib.context import CryptContext
from jose import jwt, JWTError, ExpiredSignatureError  # нужен для verify/create

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ---- пароли ----
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# ---- JWT (минимум) ----
SECRET_KEY = os.getenv("JWT_SECRET", "CHANGE_ME")
JWT_ALG    = os.getenv("JWT_ALG", "HS256")
JWT_ISS    = os.getenv("JWT_ISS", "allures-auth")
JWT_AUD    = os.getenv("JWT_AUD", "allures-api")
ACCESS_TTL_MIN = int(os.getenv("ACCESS_TTL_MIN", "15"))

def create_access_token(user_id: int, login: str, role: str = "user") -> str:
    now = int(time.time())
    payload: Dict[str, Any] = {
        "sub": str(user_id),
        "login": login,
        "role": role or "user",
        "jti": secrets.token_hex(16),
        "iat": now,
        "nbf": now,
        "exp": now + ACCESS_TTL_MIN * 60,
        "iss": JWT_ISS,
        "aud": JWT_AUD,
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=JWT_ALG)

def verify_access_token(token: str) -> Dict[str, Any]:
    return jwt.decode(
        token,
        SECRET_KEY,
        algorithms=[JWT_ALG],
        audience=JWT_AUD,
        issuer=JWT_ISS,
        options={"require_exp": True, "require_iat": True},
    )

__all__ = [
    "hash_password", "verify_password",
    "create_access_token", "verify_access_token",
]

