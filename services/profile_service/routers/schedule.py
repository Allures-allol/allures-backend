# services/profile_service/routers/schedule.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from services.profile_service.schemas.schedule import ScheduleCreate, ScheduleOut
from services.profile_service.crud.schedule import create_schedule, get_schedules
from common.db.session import get_db

router = APIRouter()

@router.post("/", response_model=ScheduleOut)
def set_schedule(data: ScheduleCreate, db: Session = Depends(get_db)):
    return create_schedule(db, data)

@router.get("/", response_model=List[ScheduleOut])
def list_schedules(db: Session = Depends(get_db)):
    return get_schedules(db)