from datetime import date, datetime

from pydantic import BaseModel


class ActivityLogCreate(BaseModel):
    steps_count: int
    log_date: date


class ActivityLogOut(BaseModel):
    id: int
    user_id: int
    steps_count: int
    calories_burned: float
    log_date: date
    created_at: datetime

    model_config = {"from_attributes": True}
