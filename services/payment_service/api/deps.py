from fastapi import Depends, HTTPException, Header
from jose import jwt, JWTError
from common.config.settings import settings

def get_current_user(x_token: str = Header(...)):
    """
    Проверка токена, аналогично auth_service
    """
    if not x_token:
        raise HTTPException(status_code=401, detail="Missing token")

    try:
        payload = jwt.decode(
            x_token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALG],
            audience=settings.JWT_AUD,
            issuer=settings.JWT_ISS
        )
        user_id = payload.get("user_id")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token payload")
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

