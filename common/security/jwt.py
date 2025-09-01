# common/security/jwt.py
import os, time, secrets
from typing import Any, Dict
from jose import jwt

SECRET_KEY = os.getenv("JWT_SECRET", "CHANGE_ME")
JWT_ALG    = os.getenv("JWT_ALG", "HS256")
JWT_ISS    = os.getenv("JWT_ISS", "allures-auth")
JWT_AUD    = os.getenv("JWT_AUD", "allures-api")

def create_access_token(*, user_id: int, expires_minutes: int, extra_claims: Dict[str, Any] | None = None) -> str:
    now = int(time.time())
    payload: Dict[str, Any] = {
        "sub": str(user_id),
        "jti": secrets.token_hex(16),
        "iat": now,
        "nbf": now,
        "exp": now + expires_minutes * 60,
        "iss": JWT_ISS,
        "aud": JWT_AUD,
    }
    if extra_claims:
        payload.update(extra_claims)
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
