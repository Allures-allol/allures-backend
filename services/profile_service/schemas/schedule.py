# services/profile_service/schemas/schedule.py
from pydantic import BaseModel
from datetime import time

class ScheduleCreate(BaseModel):
    company_id: int
    weekday: str          # вместо int — строка ("Monday", "Tuesday")
    open_time: time
    close_time: time

class ScheduleOut(ScheduleCreate):
    id: int

    class Config:
        from_attributes = True
