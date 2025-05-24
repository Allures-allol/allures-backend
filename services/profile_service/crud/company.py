# services/profile_service/crud/company.py
from services.profile_service.models.company import Company

def create_company(db, data):
    company = Company(**data.dict())
    db.add(company)
    db.commit()
    db.refresh(company)
    return company

def get_company(db):
    return db.query(Company).all()
