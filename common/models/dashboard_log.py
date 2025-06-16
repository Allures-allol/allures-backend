# common/models/dashboard_log.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from datetime import datetime
from common.db.base import Base

class DashboardLog(Base):
    __tablename__ = "dashboard_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    fetched_at = Column(DateTime, default=datetime.utcnow)
    user_agent = Column(String(255))
    notes = Column(String)  # можно использовать Text или NVARCHAR(MAX)
