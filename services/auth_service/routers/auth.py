# services/auth_service/routers/auth.py
from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from secrets import token_hex

from fastapi import APIRouter, Depends, HTTPException, Security, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from sqlalchemy import func

from common.db.session import get_db
from common.models.user import User
from common.models.session_token import SessionToken
from common.api.auth_deps import get_current_user, get_current_user_id
from common.security.jwt import create_access_token, verify_access_token  # ← JWT берём из common

from services.auth_service.utils.security import (
    hash_password,           # ← из utils только пароли
    verify_password,
)
from services.auth_service.schemas.user import (
    RegisterIn, VerifyRequestIn, VerifyConfirmIn, LoginIn, UserOut, LoginOut
)

# в Swagger отдельный “замок”
bearer_scheme_user = HTTPBearer(auto_error=False, scheme_name="UserAuth")

router = APIRouter(tags=["auth-simple"])

# --- Флаги/настройки
EMAIL_ENABLED = os.getenv("EMAIL_ENABLED", "0").strip().lower() in ("1", "true", "yes")
SESSION_TTL_MIN = int(os.getenv("SESSION_TTL_MIN", "10080"))  # 7 дней по умолчанию

# ---------- Регистрация ----------
@router.post("/register")
def register(data: RegisterIn, db: Session = Depends(get_db)):
    login_norm = (data.login or "").strip().lower()
    if "@" not in login_norm or "." not in login_norm:
        raise HTTPException(status_code=400, detail="Поле login має бути валідною e-mail адресою")

    if db.query(User.id).filter(func.lower(func.btrim(User.login)) == login_norm).first():
        raise HTTPException(status_code=409, detail="Логін вже зайнятий")
    if db.query(User.id).filter(func.lower(func.btrim(User.email)) == login_norm).first():
        raise HTTPException(status_code=409, detail="Email вже зареєстрований")

    u = User(
        login=login_norm,
        email=login_norm,
        password=hash_password(data.password),
        is_email_confirmed=not EMAIL_ENABLED,  # почта выкл → подтверждаем сразу
        is_blocked=False,
    )
    db.add(u); db.commit(); db.refresh(u)
    return {"message": "Користувача створено", "login": u.login, "email_enabled": EMAIL_ENABLED}

# ---------- Логин ----------
@router.post("/login", response_model=LoginOut)
def login(data: LoginIn, request: Request, db: Session = Depends(get_db)):
    login_norm = (data.login or "").strip().lower()
    u = db.query(User).filter(func.lower(func.btrim(User.login)) == login_norm).first()
    if not u:
        raise HTTPException(status_code=404, detail="Користувача не знайдено")
    if EMAIL_ENABLED and not u.is_email_confirmed:
        raise HTTPException(status_code=403, detail="Підтвердіть email")
    if not verify_password(data.password, u.password):
        raise HTTPException(status_code=401, detail="Невірний пароль")

    # jti + токен
    jti = token_hex(16)
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=SESSION_TTL_MIN)
    token = create_access_token(
        user_id=u.id,
        expires_minutes=SESSION_TTL_MIN,
        extra_claims={"email": u.email, "role": getattr(u, "role", "user"), "jti": jti},
    )

    # запись сессии
    user_agent = request.headers.get("user-agent")
    ip = request.client.host if request.client else None
    db.add(SessionToken(
        user_id=u.id,
        jti=jti,
        issued_at=datetime.now(timezone.utc),
        expires_at=expires_at,
        user_agent=user_agent,
        ip=ip,
        is_revoked=False,
    ))
    db.commit()

    return {
        "message": "Успішний вхід",
        "access_token": token,
        "token_type": "bearer",
        "user": UserOut.model_validate(u),
    }

# ---------- Logout ----------
@router.post("/logout")
def logout(
    credentials: HTTPAuthorizationCredentials = Security(bearer_scheme_user),  # <-- используем именованный
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    if not credentials or not credentials.credentials:
        raise HTTPException(status_code=401, detail="Missing bearer token")
    payload = verify_access_token(credentials.credentials)
    jti = payload.get("jti")
    if not jti:
        raise HTTPException(status_code=400, detail="Token missing jti")

    s = db.query(SessionToken).filter(
        SessionToken.jti == jti,
        SessionToken.user_id == user_id
    ).first()
    if not s:
        raise HTTPException(status_code=404, detail="Session not found")
    s.is_revoked = True
    db.commit()
    return {"ok": True}

@router.get("/__debug/user/{user_id}")
def dbg_user(user_id: int, db: Session = Depends(get_db)):
    u = db.query(User).filter(User.id == user_id).first()
    return {"found": bool(u), "id": u.id if u else None, "login": getattr(u, "login", None)}