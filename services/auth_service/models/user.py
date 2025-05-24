# services/auth_service/models/user.py
from pydantic import BaseModel
from common.db.base import Base

class UserCreate(BaseModel):
    login: str
    password: str
