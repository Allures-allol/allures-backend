# services/profile_service/schemas/schedule.py
from pydantic import BaseModel, conint
from datetime import time

class ScheduleCreate(BaseModel):
    weekday: conint(ge=0, le=6)
    start_time: time
    end_time: time
    is_closed: bool = False
