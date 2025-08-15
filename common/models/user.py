# common/models/user.py
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, text
from datetime import datetime
from common.db.base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    login = Column(String(255), unique=True, nullable=False)
    password = Column(Text, nullable=False)  # TEXT в БД
    full_name = Column(String(100))
    email = Column(String(255))
    phone = Column(String(30))
    avatar_url = Column(String(255))
    language = Column(String(20), default="uk")
    bonus_balance = Column(Integer, default=0)
    delivery_address = Column(String(255))
    # серверный дефолт как в БД
    registered_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
    role = Column(String(50), default="user")
    is_blocked = Column(Boolean, default=False)

    # необязательно, только ДЛЯ Alembic,чтобы «видел» частичный индекс
    # __table_args__ = (
    #     Index("uq_users_email", "email", unique=True, postgresql_where=text("email IS NOT NULL")),
    # )

