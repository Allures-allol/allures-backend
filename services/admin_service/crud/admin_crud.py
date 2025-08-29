# services/admin_service/crud/admin_crud.py
from __future__ import annotations
from typing import Optional, Tuple, List

from sqlalchemy import func, asc, desc
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from services.admin_service.schemas.admin_schemas import (
    AdminUserCreate,
    AdminUserUpdate,
    AdminPasswordChange,
    AdminUserFilter,
)
from common.models.admin import AdminUser
from common.models.payment import Payment
from common.models.user import User
from common.models.uploads import Upload
from services.admin_service.utils.security import hash_password, verify_password


# ---------- helpers ----------
def _apply_filters(q, flt: AdminUserFilter):
    if flt.email:
        q = q.filter(AdminUser.email.ilike(f"%{flt.email}%"))
    if flt.username:
        q = q.filter(AdminUser.username.ilike(f"%{flt.username}%"))
    if flt.role is not None:
        q = q.filter(AdminUser.role == flt.role.value)
    if flt.is_active is not None:
        q = q.filter(AdminUser.is_active == flt.is_active)
    if flt.subscription_status is not None:
        q = q.filter(AdminUser.subscription_status == flt.subscription_status)

    # ← новые:
    if flt.subscription_code:
        q = q.filter(AdminUser.subscription_code == flt.subscription_code)
    if flt.subscription_language:
        q = q.filter(AdminUser.subscription_language == flt.subscription_language)
    if flt.subscription_name:
        q = q.filter(AdminUser.subscription_name.ilike(f"%{flt.subscription_name}%"))

    return q


def _apply_order(q, order_by: Optional[str]):
    if not order_by:
        return q.order_by(desc(AdminUser.date_registration))
    field = order_by.lstrip("-")
    direction = desc if order_by.startswith("-") else asc
    column = getattr(AdminUser, field, None)
    if column is None:
        column = AdminUser.date_registration
    return q.order_by(direction(column))


# ---------- CRUD ----------
def create_admin_user(db: Session, admin: AdminUserCreate) -> AdminUser:
    if db.query(AdminUser).filter(AdminUser.email == admin.email).first():
        raise ValueError("DUPLICATE_EMAIL")
    if db.query(AdminUser).filter(AdminUser.username == admin.username).first():
        raise ValueError("DUPLICATE_USERNAME")

    db_admin = AdminUser(
        email=admin.email,
        username=admin.username,
        password_hash=hash_password(admin.password),
        subscription_status=admin.subscription_status,
        role=admin.role.value,
        is_active=admin.is_active,
        subscription_code=admin.subscription_code,
        subscription_language=admin.subscription_language,
        subscription_name=admin.subscription_name,
    )
    db.add(db_admin)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ValueError("UNIQUE_VIOLATION")
    db.refresh(db_admin)
    return db_admin


def get_admin_user_by_email(db: Session, email: str):
    return db.query(AdminUser).filter(AdminUser.email == email).first()


def get_admin_user_by_id(db: Session, admin_id: int):
    return db.query(AdminUser).get(admin_id)


def list_admins(db: Session, flt: AdminUserFilter) -> Tuple[List[AdminUser], int]:
    q = db.query(AdminUser)
    q = _apply_filters(q, flt)
    total = q.count()
    q = _apply_order(q, flt.order_by)
    data = q.offset((flt.page - 1) * flt.page_size).limit(flt.page_size).all()
    return data, total


def update_admin_user(db: Session, admin_id: int, patch: AdminUserUpdate) -> AdminUser:
    db_admin = get_admin_user_by_id(db, admin_id)
    if not db_admin:
        raise LookupError("NOT_FOUND")

    if patch.email and patch.email != db_admin.email:
        if db.query(AdminUser).filter(AdminUser.email == patch.email).first():
            raise ValueError("DUPLICATE_EMAIL")

    if patch.username and patch.username != db_admin.username:
        if db.query(AdminUser).filter(AdminUser.username == patch.username).first():
            raise ValueError("DUPLICATE_USERNAME")

    for field, value in patch.model_dump(exclude_unset=True).items():
        if field == "role" and value is not None:
            setattr(db_admin, field, value.value)
        else:
            setattr(db_admin, field, value)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ValueError("UNIQUE_VIOLATION")

    db.refresh(db_admin)
    return db_admin


def change_admin_password(db: Session, admin_id: int, body: AdminPasswordChange) -> None:
    db_admin = get_admin_user_by_id(db, admin_id)
    if not db_admin:
        raise LookupError("NOT_FOUND")

    if not verify_password(body.old_password, db_admin.password_hash):
        raise PermissionError("BAD_OLD_PASSWORD")

    db_admin.password_hash = hash_password(body.new_password)
    db.commit()


def get_admin_stats(db: Session) -> dict:
    try:
        upload_count = db.query(func.count(Upload.id)).scalar() or 0
    except Exception:
        upload_count = 0

    try:
        users_count = db.query(func.count(User.id)).scalar() or 0
    except Exception:
        users_count = 0

    try:
        revenue_total = db.query(func.coalesce(func.sum(Payment.amount), 0)).scalar() or 0
        revenue_total = float(revenue_total)
    except Exception:
        revenue_total = 0.0

    return {
        "upload_count": upload_count,
        "users_count": users_count,
        "revenue_total": revenue_total,
    }
