# services/profile_service/routers/schedule.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from services.profile_service.schemas.schedule import ScheduleCreate
from services.profile_service.crud.schedule import create_schedule
from common.db.session import get_db

router = APIRouter()

@router.post("/")
def set_schedule(data: ScheduleCreate, db: Session = Depends(get_db)):
    return create_schedule(db, data)