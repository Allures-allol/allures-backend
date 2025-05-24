# services/profile_service/models/schedule.py
from sqlalchemy import Column, Integer, Boolean, Time
from common.db.base import Base

class Schedule(Base):
    __tablename__ = "schedules"
    id = Column(Integer, primary_key=True)
    weekday = Column(Integer)
    start_time = Column(Time)
    end_time = Column(Time)
    is_closed = Column(Boolean, default=False)
