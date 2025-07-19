# services/admin_service/crud/admin_crud.py
from sqlalchemy.orm import Session, joinedload
from services.admin_service.schemas import admin_schemas
from common.models.admin import AdminUser
from common.models.subscriptions import Subscription, UserSubscription
from common.models.payment import Payment

from services.subscription_service.utils.security import hash_password

# Создание администратора с хешированием пароля
def create_admin_user(db: Session, admin: admin_schemas.AdminUserCreate):
    hashed_pw = hash_password(admin.password)

    db_admin = AdminUser(
        email=admin.email,
        username=admin.username,
        password_hash=hashed_pw,
        subscription_status=admin.subscription_status
    )
    db.add(db_admin)
    db.commit()
    db.refresh(db_admin)
    return db_admin

def get_admin_user_by_email(db: Session, email: str):
    return db.query(AdminUser).filter(AdminUser.email == email).first()

# Все админы
def get_all_admins(db: Session):
    return db.query(AdminUser).all()

# Все платежи
def get_payments(db: Session):
    return db.query(Payment).options(joinedload(Payment.user)).all()

# Платежи конкретного пользователя
def get_payments_by_user_id(db: Session, user_id: int):
    return db.query(Payment).filter(Payment.user_id == user_id).all()
