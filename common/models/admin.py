# common/models/admin.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Index
from sqlalchemy.sql import func
from common.db.base import Base

class AdminUser(Base):
    __tablename__ = "admin_users"

    id = Column(Integer, primary_key=True, index=True)

    # учётка
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)

    # статус
    subscription_status = Column(Boolean, nullable=False, default=False)
    role = Column(String(32), nullable=False, default="admin")
    is_active = Column(Boolean, nullable=False, default=True)

    # даты
    date_registration = Column(DateTime(timezone=True), server_default=func.now())
    last_login_date = Column(DateTime(timezone=True), nullable=True)

    # --- СНИМОК подписки у админа (опционально, для отображения/фильтра) ---
    subscription_code = Column(String(50), nullable=True)      # например: basic|advanced|premium|free
    subscription_language = Column(String(5), nullable=True)   # uk|ru|en
    subscription_name = Column(String(50), nullable=True)      # “Преміум”, “Advanced”, и т.п.

# удобные индексы для фильтрации
Index("ix_admin_users_subs_code", AdminUser.subscription_code)
Index("ix_admin_users_subs_lang", AdminUser.subscription_language)
Index("ix_admin_users_subs_name", AdminUser.subscription_name)