# common/models/schedule.py

from sqlalchemy import Column, Integer, String, Time, ForeignKey
from sqlalchemy.orm import relationship
from common.db.base import Base

class Schedule(Base):
    __tablename__ = "schedules"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)

    # В БД: weekday VARCHAR(50), open_time TIME, close_time TIME
    weekday = Column(String(50), nullable=False)
    open_time = Column(Time, nullable=False)
    close_time = Column(Time, nullable=False)

    # можно связать с Company (не обязательно)
    company = relationship("Company", backref="schedules")
