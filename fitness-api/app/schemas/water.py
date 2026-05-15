from datetime import date, datetime

from pydantic import BaseModel


class WaterLogCreate(BaseModel):
    amount_ml: float
    log_date: date


class WaterLogOut(BaseModel):
    id: int
    user_id: int
    amount_ml: float
    log_date: date
    created_at: datetime

    model_config = {"from_attributes": True}
