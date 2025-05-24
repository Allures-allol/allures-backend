# services/profile_service/routers/company.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from services.profile_service.schemas.company import CompanyCreate, CompanyOut
from services.profile_service.crud.company import create_company, get_company
from common.db.session import get_db

router = APIRouter()

@router.post("/", response_model=CompanyOut)
def create(data: CompanyCreate, db: Session = Depends(get_db)):
    return create_company(db, data)

@router.get("/", response_model=list[CompanyOut])
def read_all(db: Session = Depends(get_db)):
    return get_company(db)
