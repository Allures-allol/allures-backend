# services/profile_service/schemas/company.py
from pydantic import BaseModel

class CompanyCreate(BaseModel):
    name: str
    description: str
    email: str
    phone: str

class CompanyOut(CompanyCreate):
    id: int
    class Config:
        from_attributes = True
