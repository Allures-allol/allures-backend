# services/auth_service/routers/auth.py
from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy import func
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta, timezone
import smtplib
from email.message import EmailMessage
import jwt

from services.auth_service.schemas.user import (
    UserCreate, ForgotPassword, ResetPassword, UserOut,
    LoginRequest, LoginResponse, UserProfileOut, UserProfileUpdate
)
from services.auth_service.crud.user import (
    create_user, authenticate_user, forgot_password,
    reset_password, get_all_users, delete_user_by_id
)
from services.auth_service.utils.security import hash_password, create_access_token
from common.db.session import get_db
from common.models.user import User
from services.auth_service.deps.auth import get_current_user
from common.config.settings import settings

router = APIRouter()

# ---------- helpers: email + token ----------
def _create_email_token(user_id: int, ttl_hours: int = 24) -> str:
    payload = {
        "sub": str(user_id),
        "typ": "email_confirm",
        "iss": getattr(settings, "JWT_ISS", "allures-auth"),
        "aud": getattr(settings, "JWT_AUD", "allures-api"),
        "exp": datetime.now(tz=timezone.utc) + timedelta(hours=ttl_hours),
        "iat": datetime.now(tz=timezone.utc),
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALG)

def _send_mail(to_email: str, subject: str, html: str, text: Optional[str] = None) -> None:
    host = getattr(settings, "SMTP_HOST", None)
    port = int(getattr(settings, "SMTP_PORT", 587))
    user = getattr(settings, "SMTP_USER", None)
    pwd  = getattr(settings, "SMTP_PASSWORD", None)
    mail_from = getattr(settings, "MAIL_FROM", "no-reply@local")
    mail_from_name = getattr(settings, "MAIL_FROM_NAME", "Allures")

    if not host or not user or not pwd:
        # безопасный фоллбек: просто логируем (не падаем при отсутствии SMTP)
        print(f"[MAIL] to={to_email} subject={subject}\n{text or ''}\n----\n{html}\n")
        return

    msg = EmailMessage()
    msg["From"] = f"{mail_from_name} <{mail_from}>"
    msg["To"] = to_email
    msg["Subject"] = subject
    if text:
        msg.set_content(text)
    msg.add_alternative(html, subtype="html")

    with smtplib.SMTP(host, port) as s:
        s.starttls()
        s.login(user, pwd)
        s.send_message(msg)

def _build_confirm_link(token: str) -> str:
    base = getattr(settings, "AUTH_PUBLIC_URL", None)
    # по умолчанию пробуем собрать из AUTH_SERVICE_URL + /auth
    if not base:
        origin = getattr(settings, "AUTH_SERVICE_URL", "http://127.0.0.1:8003").rstrip("/")
        base = f"{origin}/auth"
    return f"{base}/confirm-email?token={token}"

# --- Регистрация ---
@router.post("/register", response_model=UserOut)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    # нормализация входных
    login_norm  = (user.login or "").strip()
    email_input = (getattr(user, "email", None) or "").strip().lower()

    # если email не передан, но login похож на e-mail — используем его
    if not email_input:
        if "@" in login_norm and "." in login_norm:
            email_input = login_norm.lower()
        else:
            raise HTTPException(status_code=400, detail="Email обязателен для подтверждения регистрации")

    # уникальность логина и email
    if db.query(User).filter(User.login == login_norm).first():
        raise HTTPException(status_code=409, detail="Логин уже занят")
    if db.query(User).filter(func.lower(func.btrim(User.email)) == email_input).first():
        raise HTTPException(status_code=409, detail="Email уже зарегистрирован")

    # создание пользователя
    hashed_pw = hash_password(user.password)
    db_user = User(
        login=login_norm,
        email=email_input,
        password=hashed_pw,
        is_email_confirmed=False,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    # письмо с подтверждением (в DEV при отсутствии SMTP просто залогируется ссылка)
    try:
        token = _create_email_token(db_user.id)
        link = _build_confirm_link(token)
        subj = "Підтвердження реєстрації | Allures"
        html = f"""
        <p>Вітаємо, {db_user.login}!</p>
        <p>Щоб підтвердити email, перейдіть за посиланням:</p>
        <p><a href="{link}">{link}</a></p>
        <p>Посилання дійсне 24 години.</p>
        """
        _send_mail(db_user.email, subj, html, text=f"Confirm: {link}")
        resp = db_user
        if getattr(settings, "EMAIL_DEBUG_RETURN_TOKEN", "0") == "1":
            resp = {**UserOut.from_orm(db_user).dict(), "debug_token": token, "confirm_link": link}
        return resp
    except Exception as e:
        # не валим регистрацию
        print(f"[MAIL][register] send error: {e}")

    return db_user


@router.get("/dev/make-confirm-token")
def dev_make_token(user_id: int, db: Session = Depends(get_db)):
    if getattr(settings, "AUTH_DEV_CONFIRM", "0") != "1":
        raise HTTPException(404, "Not found")
    u = db.query(User).filter(User.id == user_id).first()
    if not u:
        raise HTTPException(404, "User not found")
    token = _create_email_token(u.id)
    return {"token": token, "confirm_url": _build_confirm_link(token)}

# --- Подтверждение email ---
@router.get("/confirm-email")
def confirm_email(token: str = Query(...), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALG],
            audience=getattr(settings, "JWT_AUD", "allures-api"),
            issuer=getattr(settings, "JWT_ISS", "allures-auth"),
        )
        if payload.get("typ") != "email_confirm":
            raise HTTPException(status_code=400, detail="Неверный тип токена")
        user_id = int(payload.get("sub"))
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=400, detail="Токен просрочен")
    except Exception:
        raise HTTPException(status_code=400, detail="Невалидный токен")

    u = db.query(User).filter(User.id == user_id).first()
    if not u:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    if not u.is_email_confirmed:
        u.is_email_confirmed = True
        db.commit()
        db.refresh(u)

    return {"message": "Email підтверджено", "user_id": u.id}

# --- Повторная отправка письма ---
@router.post("/resend-confirmation")
def resend_confirmation(email: str = Query(...), db: Session = Depends(get_db)):
    u = db.query(User).filter(User.email == email).first()
    if not u:
        raise HTTPException(status_code=404, detail="Користувача з таким email не знайдено")
    if u.is_email_confirmed:
        return {"message": "Email вже підтверджено"}

    try:
        token = _create_email_token(u.id)
        link = _build_confirm_link(token)
        subj = "Підтвердження реєстрації (повторно) | Allures"
        html = f"""
        <p>Вітаємо, {u.login}!</p>
        <p>Щоб підтвердити email, перейдіть за посиланням:</p>
        <p><a href="{link}">{link}</a></p>
        <p>Посилання дійсне 24 години.</p>
        """
        _send_mail(u.email, subj, html, text=f"Confirm: {link}")
    except Exception as e:
        print(f"[MAIL][resend] send error: {e}")
        raise HTTPException(status_code=500, detail="Не вдалося відправити лист")

    return {"message": "Лист відправлено"}

# --- Логин (блокируем, если email не подтвержден) ---
@router.post("/login", response_model=LoginResponse)
def login(user: LoginRequest, db: Session = Depends(get_db)):
    user_obj = authenticate_user(db, user.login, user.password)
    if not user_obj.is_email_confirmed:
        raise HTTPException(status_code=403, detail="Підтвердіть email, будь ласка")

    token = create_access_token(user_obj.id, user_obj.login, user_obj.role)
    return LoginResponse(
        access_token=token,
        token_type="bearer",
        id=user_obj.id,
        login=user_obj.login,
        role=user_obj.role,
        registered_at=user_obj.registered_at,
        is_blocked=user_obj.is_blocked
    )


# --- Получение текущего профиля ---
@router.get("/me", response_model=UserOut)
def get_profile_me(current_user: User = Depends(get_current_user)):
    return current_user

# --- Сброс пароля ---
@router.post("/forgot-password")
def forgot(user: ForgotPassword, db: Session = Depends(get_db)):
    return forgot_password(db, user.email)


@router.post("/reset-password")
def reset(user: ResetPassword, db: Session = Depends(get_db)):
    return reset_password(db, user.email, user.new_password)


# --- Список всех пользователей (только для админа позже) ---
@router.get("/users", response_model=List[UserOut], dependencies=[Depends(get_current_user)])
def list_users(db: Session = Depends(get_db)):
    return get_all_users(db)


# --- Получение пользователя по ID ---
@router.get("/users/{user_id}", response_model=UserOut, dependencies=[Depends(get_current_user)])
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Користувача не знайдено")
    return user


# --- Обновление профиля пользователя ---
@router.patch("/users/{user_id}", summary="Оновити дані користувача", dependencies=[Depends(get_current_user)])
def patch_user_profile(
    user_id: int,
    profile_data: UserProfileUpdate,
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Користувача не знайдено")

    for field, value in profile_data.dict(exclude_unset=True).items():
        setattr(user, field, value)

    db.commit()
    db.refresh(user)
    return {"message": "Профіль оновлено", "user_id": user_id}


# --- Удаление пользователя ---
@router.delete("/users/{user_id}", dependencies=[Depends(get_current_user)])
def delete_user(user_id: int, db: Session = Depends(get_db)):
    success = delete_user_by_id(db, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Користувача не знайдено або вже видалено")
    return {"message": f"Користувач {user_id} успішно видалений"}
