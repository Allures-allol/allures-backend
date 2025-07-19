# services/admin_service/routers/admin_router.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func

from common.db.session import get_db
from common.models.admin import AdminUser
from common.models.uploads import Upload
from common.models.subscriptions import Subscription, UserSubscription
from common.models.payment import Payment

from services.admin_service.schemas.admin_schemas import AdminUserCreate, AdminUserOut, AdminLogin
from services.admin_service.crud import admin_crud
from services.subscription_service.utils.security import verify_password
from services.subscription_service.routers.subscription_routers import activate_subscription

router = APIRouter()


@router.post("/create", response_model=AdminUserOut)
def create_admin(admin: AdminUserCreate, db: Session = Depends(get_db)):
    return admin_crud.create_admin_user(db, admin)

@router.post("/login", response_model=AdminUserOut)
def login_admin(credentials: AdminLogin, db: Session = Depends(get_db)):
    print(f" Попытка входа: {credentials.email}")
    admin = admin_crud.get_admin_user_by_email(db, credentials.email)

    if not admin:
        print(" Админ не найден в базе")
        raise HTTPException(status_code=401, detail="Неверный логин или пароль")

    if not verify_password(credentials.password, admin.password_hash):
        print(" Неверный пароль")
        raise HTTPException(status_code=401, detail="Неверный логин или пароль")

    print(f" Успешный вход: {admin.username}")
    return admin


@router.get("/all", response_model=list[AdminUserOut])
def get_all_admins(db: Session = Depends(get_db)):
    return admin_crud.get_all_admins(db)


@router.get("/{admin_id}/stats")
def get_admin_stats(admin_id: int, db: Session = Depends(get_db)):

    upload_count = db.query(func.count(Upload.id)).scalar()
    return {"upload_count": upload_count}


@router.post("/activate-subscription")
def activate_subscription(user_id: int, payment_id: int, db: Session = Depends(get_db)):
    activate_subscription(user_id=user_id, payment_id=payment_id, db=db)
    return {"message": "Подписка успешно активирована"}

