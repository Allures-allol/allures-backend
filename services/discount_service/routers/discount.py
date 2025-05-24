from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from services.discount_service.schemas.discount import DiscountCreate, DiscountOut
from services.discount_service.crud.discount import create_discount, get_valid_discounts
from common.db.session import get_db

router = APIRouter()

@router.post("/", response_model=DiscountOut)
def create(data: DiscountCreate, db: Session = Depends(get_db)):
    return create_discount(db, data)

@router.get("/", response_model=list[DiscountOut])
def read_all(db: Session = Depends(get_db)):
    return get_valid_discounts(db)