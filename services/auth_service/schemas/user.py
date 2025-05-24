# services/common/schemas/user.py
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class UserCreate(BaseModel):
    login: str
    password: str

class UserOut(BaseModel):
    id: int
    login: str
    registered_at: datetime
    role: Optional[str] = "user"
    is_blocked: Optional[bool] = False

    class Config:
        from_attributes = True


