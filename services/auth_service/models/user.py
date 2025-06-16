# services/auth_service/models/user.py
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional

class UserCreate(BaseModel):
    login: str = Field(..., example="user@example.com")
    password: str = Field(..., example="Password123")

class UserOut(BaseModel):
    id: int
    login: str
    full_name: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    avatar_url: Optional[str]
    language: Optional[str]
    bonus_balance: Optional[int]
    delivery_address: Optional[str]
    registered_at: datetime
    role: Optional[str] = "user"
    is_blocked: Optional[bool] = False

    class Config:
        from_attributes = True

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    login: str
    role: str
    registered_at: datetime
    id: int
    is_blocked: bool

class ForgotPassword(BaseModel):
    email: EmailStr

class ResetPassword(BaseModel):
    email: EmailStr
    new_password: str
