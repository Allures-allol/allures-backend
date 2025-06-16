# services/discount_service/routers/discount.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from services.discount_service.schemas.discount import DiscountCreate, DiscountOut
from services.discount_service.crud.discount import create_discount, get_valid_discounts
from common.db.session import get_db

router = APIRouter()

@router.post("/", response_model=DiscountOut, status_code=status.HTTP_201_CREATED)
def create_discount_endpoint(data: DiscountCreate, db: Session = Depends(get_db)):
    """
    Создание новой скидки
    """
    return create_discount(db, data)

@router.get("/", response_model=list[DiscountOut])
def read_all_discounts(db: Session = Depends(get_db)):
    """
    Получение всех актуальных скидок
    """
    return get_valid_discounts(db)
