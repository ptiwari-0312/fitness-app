from pydantic import BaseModel


class DashboardOut(BaseModel):
    bmr: float
    tdee: float
    calories_consumed: float
    calories_burned: float
    net_calories: float
