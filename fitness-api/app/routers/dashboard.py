from datetime import date, datetime
from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.activity_log import ActivityLog
from app.models.food_log import FoodLog
from app.models.user import User
from app.schemas.dashboard import DashboardOut
from app.services.bmr_service import calculate_bmr, calculate_tdee
from app.utils.dependencies import get_current_user

router = APIRouter(prefix="/api/v1/dashboard", tags=["dashboard"])


@router.get("/summary", response_model=DashboardOut)
def get_summary(
    log_date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    target_date = log_date or datetime.utcnow().date()

    bmr = calculate_bmr(current_user.weight_kg, current_user.height_cm, current_user.age, current_user.gender)
    tdee = calculate_tdee(bmr, current_user.activity_level)

    food_logs = (
        db.query(FoodLog)
        .filter(FoodLog.user_id == current_user.id, FoodLog.log_date == target_date)
        .all()
    )
    calories_consumed = sum(
        log.food_item.calories_per_100g * log.quantity_grams / 100
        for log in food_logs
    )

    activity_logs = (
        db.query(ActivityLog)
        .filter(ActivityLog.user_id == current_user.id, ActivityLog.log_date == target_date)
        .all()
    )
    calories_burned = sum(log.calories_burned for log in activity_logs)

    return DashboardOut(
        bmr=round(bmr, 2),
        tdee=round(tdee, 2),
        calories_consumed=round(calories_consumed, 2),
        calories_burned=round(calories_burned, 2),
        net_calories=round(calories_consumed - calories_burned, 2),
    )
