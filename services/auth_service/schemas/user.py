from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional

class UserCreate(BaseModel):
    login: str = Field(..., example="user@example.com")
    password: str = Field(..., example="yourStrongPassword123")

class UserOut(BaseModel):
    id: int
    login: str
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


