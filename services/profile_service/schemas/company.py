# services/profile_service/schemas/company.py
from pydantic import BaseModel

class CompanyBase(BaseModel):
    name: str
    description: str | None = None

class CompanyCreate(CompanyBase):
    pass

class CompanyOut(CompanyBase):
    id: int

    class Config:
        orm_mode = True