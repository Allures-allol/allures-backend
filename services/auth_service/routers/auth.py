from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Security
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta, timezone
from email.message import EmailMessage
from typing import Optional
import os, smtplib, secrets

from common.db.session import get_db
from common.models.user import User
from services.auth_service.utils.security import hash_password, verify_password
from services.auth_service.schemas.user import (
    RegisterIn, VerifyRequestIn, VerifyConfirmIn, LoginIn, UserOut
)

# Если в app main НЕТ root_path="/auth":
# router = APIRouter(prefix="/auth", tags=["auth-simple"])
# Если root_path="/auth", то так:
router = APIRouter(prefix="", tags=["auth-simple"])

# ---------- Mailpit / config ----------
SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT"))
MAIL_FROM = os.getenv("MAIL_FROM")
MAIL_FROM_NAME = os.getenv("MAIL_FROM_NAME")
EMAIL_CODE_TTL_MIN = int(os.getenv("EMAIL_CODE_TTL_MIN"))

def _now_utc() -> datetime:
    return datetime.now(tz=timezone.utc)

def _gen_code(n: int = 6) -> str:
    return f"{secrets.randbelow(10**n):0{n}d}"

def _send_mail(to_email: str, subject: str, html: str, text: Optional[str] = None):
    SMTP_USER = os.getenv("SMTP_USER")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
    
    msg = EmailMessage()
    msg["From"] = f"{MAIL_FROM_NAME} <{MAIL_FROM}>"
    msg["To"] = to_email
    msg["Subject"] = subject
    if text:
        msg.set_content(text)
    msg.add_alternative(html, subtype="html")
    
    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as s:
            s.ehlo()
            s.starttls()
            s.ehlo()
            s.login(SMTP_USER, SMTP_PASSWORD)
            s.send_message(msg)
        print(f"[MAIL] sent to {to_email}")
    except smtplib.SMTPException as e:
        print(f"[MAIL] SMTP error: {repr(e)}")
    except Exception as e:
        print(f"[MAIL] other error: {repr(e)}")


# ---------- Admin guard (для CRUD) ----------
admin_scheme = HTTPBearer(description="Service Admin JWT", auto_error=False)

def admin_guard(credentials: HTTPAuthorizationCredentials = Security(admin_scheme)):
    admin_jwt = os.getenv("ADMIN_JWT", "")
    if not admin_jwt:
        raise HTTPException(status_code=500, detail="ADMIN_JWT is not configured")
    if not credentials or not credentials.credentials:
        raise HTTPException(status_code=401, detail="Missing admin bearer token")
    if credentials.credentials != admin_jwt:
        raise HTTPException(status_code=403, detail="Invalid admin token")

# ---------- Регистрация (login=email + password) ----------
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
        is_email_confirmed=False,
        is_blocked=False,
    )
    db.add(u)
    db.flush()  # получим u.id

    code = _gen_code(6)
    u.email_code = code
    u.email_code_expires_at = _now_utc() + timedelta(minutes=EMAIL_CODE_TTL_MIN)
    u.email_code_sent_at = _now_utc()
    u.email_code_attempts = 0

    db.commit()
    db.refresh(u)

    subj = "Підтвердження e-mail | Allures"
    html = f"""
    <p>Вітаємо!</p>
    <p>Ваш код підтвердження: <strong style="font-size:20px">{code}</strong></p>
    <p>Код дійсний {EMAIL_CODE_TTL_MIN} хвилин.</p>
    """
    _send_mail(u.email, subj, html, text=f"Verification code: {code}")

    return {"message": "Користувача створено, код відправлено на пошту", "login": u.login}

# ---------- Повторная отправка кода ----------
@router.post("/verify/request")
def verify_request(data: VerifyRequestIn, db: Session = Depends(get_db)):
    login_norm = (data.login or "").strip().lower()
    u = db.query(User).filter(func.lower(func.btrim(User.login)) == login_norm).first()
    if not u:
        raise HTTPException(status_code=404, detail="Користувача не знайдено")
    if u.is_email_confirmed:
        return {"message": "Email вже підтверджено"}

    if u.email_code_sent_at and (_now_utc() - u.email_code_sent_at).total_seconds() < 30:
        raise HTTPException(status_code=429, detail="Занадто часто, спробуйте пізніше")

    code = _gen_code(6)
    u.email_code = code
    u.email_code_expires_at = _now_utc() + timedelta(minutes=EMAIL_CODE_TTL_MIN)
    u.email_code_sent_at = _now_utc()
    u.email_code_attempts = 0
    db.commit()

    subj = "Підтвердження e-mail | Allures (повторно)"
    html = f"""
    <p>Ваш новий код: <strong style="font-size:20px">{code}</strong></p>
    <p>Код дійсний {EMAIL_CODE_TTL_MIN} хвилин.</p>
    """
    _send_mail(u.email, subj, html, text=f"Verification code: {code}")
    return {"message": "Код повторно відправлено"}

# ---------- Подтверждение кода ----------
@router.post("/verify/confirm")
def verify_confirm(data: VerifyConfirmIn, db: Session = Depends(get_db)):
    login_norm = (data.login or "").strip().lower()
    u = db.query(User).filter(func.lower(func.btrim(User.login)) == login_norm).first()
    if not u:
        raise HTTPException(status_code=404, detail="Користувача не знайдено")
    if u.is_email_confirmed:
        return {"message": "Email вже підтверджено"}

    if (u.email_code_attempts or 0) >= 5:
        raise HTTPException(status_code=429, detail="Забагато спроб, надішліть код знову")

    if not u.email_code or not u.email_code_expires_at or _now_utc() > u.email_code_expires_at:
        raise HTTPException(status_code=400, detail="Код прострочено, надішліть код знову")

    if (data.code or "").strip() != u.email_code:
        u.email_code_attempts = (u.email_code_attempts or 0) + 1
        db.commit()
        raise HTTPException(status_code=400, detail="Невірний код")

    u.is_email_confirmed = True
    u.email_code = None
    u.email_code_expires_at = None
    u.email_code_sent_at = None
    u.email_code_attempts = 0
    db.commit()

    return {"message": "Email підтверджено"}

# ---------- Логин ----------
@router.post("/login")
def login(data: LoginIn, db: Session = Depends(get_db)):
    login_norm = (data.login or "").strip().lower()
    u = db.query(User).filter(func.lower(func.btrim(User.login)) == login_norm).first()
    if not u:
        raise HTTPException(status_code=404, detail="Користувача не знайдено")
    if not u.is_email_confirmed:
        raise HTTPException(status_code=403, detail="Підтвердіть email")

    if not verify_password(data.password, u.password):
        raise HTTPException(status_code=401, detail="Невірний пароль")

    return {"message": "Успішний вхід", "user": UserOut.model_validate(u)}

# ---------- CRUD пользователей (только сервисный токен) ----------
@router.get("/users", response_model=list[UserOut])
def list_users(
    db: Session = Depends(get_db),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    _=Security(admin_guard),  # именно Security, чтобы Swagger показал Authorize
):
    return db.query(User).order_by(User.id.asc()).limit(limit).offset(offset).all()

@router.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    _=Security(admin_guard),
):
    u = db.query(User).filter(User.id == user_id).first()
    if not u:
        raise HTTPException(status_code=404, detail="Користувача не знайдено або вже видалено")
    db.delete(u)
    db.commit()
    return {"message": f"Користувач {user_id} успішно видалений"}
