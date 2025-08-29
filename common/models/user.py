# common/models/user.py  (добавь поля, чтобы ORM их «видел»)
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, text
from datetime import datetime
from common.db.base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    is_email_confirmed = Column(Boolean, nullable=False, default=False)
    login = Column(String(255), unique=True, nullable=False)
    password = Column(Text, nullable=False)
    full_name = Column(String(100))
    email = Column(String(255))
    phone = Column(String(30))
    avatar_url = Column(String(255))
    language = Column(String(20), default="uk")
    bonus_balance = Column(Integer, default=0)
    delivery_address = Column(String(255))
    registered_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
    role = Column(String(50), default="user")
    is_blocked = Column(Boolean, default=False)

    #  поля для одноразового кода подтверждения
    email_code = Column(String(7))                     # сам код (6–7 знаков)
    email_code_expires_at = Column(DateTime(timezone=True))
    email_code_sent_at = Column(DateTime(timezone=True))
    email_code_attempts = Column(Integer, default=0)
