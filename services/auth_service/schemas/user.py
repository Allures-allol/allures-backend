from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional

# ------ Регистрация / подтверждение кода ------
class RegisterIn(BaseModel):
    login: str = Field(..., example="user@example.com")
    password: str = Field(..., min_length=6, example="YourStrongPassword123!")

class VerifyRequestIn(BaseModel):
    login: str = Field(..., example="user@example.com")

class VerifyConfirmIn(BaseModel):
    login: str = Field(..., example="user@example.com")
    code: str = Field(..., min_length=6, max_length=7, example="123456")

class LoginIn(BaseModel):
    login: str = Field(..., example="user@example.com")
    password: str = Field(..., example="YourStrongPassword123!")

# ------ Вывод пользователя ------
class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    login: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    role: Optional[str] = "user"
    registered_at: Optional[datetime] = None
    is_blocked: Optional[bool] = False
    is_email_confirmed: Optional[bool] = False
