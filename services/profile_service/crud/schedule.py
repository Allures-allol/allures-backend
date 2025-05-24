# services/profile_service/crud/schedule.py
from services.profile_service.models.schedule import Schedule

def create_schedule(db, data):
    obj = Schedule(**data.dict())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj