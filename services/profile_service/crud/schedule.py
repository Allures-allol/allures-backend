# services/profile_service/crud/schedule.py
from sqlalchemy.orm import Session
from services.profile_service.schemas.schedule import ScheduleCreate
from common.models.schedule import Schedule

def create_schedule(db: Session, data: ScheduleCreate) -> Schedule:
    obj = Schedule(**data.dict())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

def get_schedules(db: Session):
    return db.query(Schedule).all()
