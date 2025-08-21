# services/subscription_service/utils/security.py

from __future__ import annotations

import os

import jwt  # PyJWT
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from typing import Optional
from fastapi import Depends, Header


# ---- Настройки из окружения ----
JWT_SECRET = os.getenv("JWT_SECRET", "")
JWT_ALG = os.getenv("JWT_ALG", "HS256")
JWT_AUD = os.getenv("JWT_AUD")            # опционально
JWT_ISS = os.getenv("JWT_ISS")            # опционально

# эндпоинт авторизации в auth_service (если используешь OAuth2PasswordBearer)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


class TokenError(HTTPException):
    def __init__(self, detail: str = "Could not validate token"):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail, headers={"WWW-Authenticate": "Bearer"})

def get_user_id_optional(authorization: Optional[str] = Header(None)) -> Optional[int]:
    if not authorization or not authorization.lower().startswith("bearer "):
        return None
    token = authorization.split(" ", 1)[1]
    payload = _decode_token(token)
    return get_user_id_from_payload(payload)


def _decode_token(token: str) -> dict:
    if not JWT_SECRET:
        raise TokenError("JWT secret is not configured")

    options = {"verify_aud": bool(JWT_AUD)}
    kwargs = {"algorithms": [JWT_ALG]}
    if JWT_AUD:
        kwargs["audience"] = JWT_AUD
    if JWT_ISS:
        kwargs["issuer"] = JWT_ISS

    try:
        payload = jwt.decode(token, JWT_SECRET, options=options, **kwargs)
        return payload
    except jwt.ExpiredSignatureError:
        raise TokenError("Token expired")
    except jwt.InvalidTokenError:
        raise TokenError("Invalid token")


def get_user_id_from_payload(payload: dict) -> int:
    """
    Стандартно берём из 'sub'. Фоллбек — 'user_id'.
    """
    val = payload.get("sub", payload.get("user_id"))
    try:
        return int(val)
    except (TypeError, ValueError):
        raise TokenError("Token subject is missing or invalid")


# ---- FastAPI dependency ----
def get_current_user_id(token: str = Depends(oauth2_scheme)) -> int:
    payload = _decode_token(token)
    return get_user_id_from_payload(payload)


# ---- Удобные помощники если нужно вручную проверять токен ----
def verify_bearer_token(token: str) -> int:
    """
    Прямая проверка без FastAPI Depends.
    Возвращает user_id или бросает HTTP 401.
    """
    payload = _decode_token(token)
    return get_user_id_from_payload(payload)
