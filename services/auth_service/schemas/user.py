# services/auth_service/schemas/user.py
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional

class UserCreate(BaseModel):
    login: str = Field(..., example="user@example.com")
    password: str = Field(..., example="yourStrongPassword123")
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    avatar_url: Optional[str] = None
    language: Optional[str] = "uk"
    bonus_balance: Optional[int] = 0
    delivery_address: Optional[str] = None
    role: Optional[str] = "user"
    is_blocked: Optional[bool] = False

class UserOut(BaseModel):
    id: int
    login: str
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    avatar_url: Optional[str] = None
    language: Optional[str] = None
    bonus_balance: Optional[int] = 0
    delivery_address: Optional[str] = None
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


