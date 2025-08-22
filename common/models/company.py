# common/models/company.py
from sqlalchemy import Column, Integer, String
from common.db.base import Base

class Company(Base):
    __tablename__ = "companies"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    description = Column(String)
