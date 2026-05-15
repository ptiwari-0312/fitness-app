from datetime import date

from pydantic import BaseModel


class DashboardOut(BaseModel):
    bmr: float
    tdee: float
    calories_consumed: float
    calories_burned: float
    net_calories: float
    protein_g: float
    carbs_g: float
    fat_g: float


class WeeklyTrendDay(BaseModel):
    log_date: date
    net_calories: float
    has_data: bool
