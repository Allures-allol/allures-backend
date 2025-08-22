# services/profile_service/crud/company.py
from common.models.company import Company
from sqlalchemy.orm import Session


def create_company(db, data):
    company = Company(**data.dict())
    db.add(company)
    db.commit()
    db.refresh(company)
    return company

def get_company(db):
    return db.query(Company).all()
