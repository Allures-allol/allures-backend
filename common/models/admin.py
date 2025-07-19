from sqlalchemy import Column, Integer, String, DateTime, Boolean
from datetime import datetime
from common.db.base import Base

class AdminUser(Base):
    __tablename__ = "admin_user"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False)
    username = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    subscription_status = Column(Boolean, default=False)
    date_registration = Column(DateTime, default=datetime.utcnow)
    last_login_date = Column(DateTime, default=datetime.utcnow)

