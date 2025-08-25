# services/auth_service/schemas/user.py
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional

class UserCreate(BaseModel):
    login: str = Field(..., example="user@example.com")
    password: str = Field(..., example="yourStrongPassword123")
    email: Optional[str] = None

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
        class Config:
            orm_mode = True

class LoginRequest(BaseModel):
    login: str = Field(..., example="user@example.com")
    password: str = Field(..., example="yourStrongPassword123")

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    login: str
    role: str
    registered_at: datetime
    id: int
    is_blocked: bool

class UserProfileUpdate(BaseModel):
    full_name: Optional[str]
    email: Optional[EmailStr]
    phone: Optional[str]
    avatar_url: Optional[str]
    language: Optional[str]
    bonus_balance: Optional[int]
    delivery_address: Optional[str]

class UserProfileOut(BaseModel):
    id: int
    login: str
    full_name: Optional[str] = None
    email: Optional[str] = None
    role: str
    registered_at: Optional[datetime] = None
    is_blocked: Optional[bool] = None

    class Config:
        orm_mode = True
class ForgotPassword(BaseModel):
    email: EmailStr

class ResetPassword(BaseModel):
    email: EmailStr
    new_password: str
