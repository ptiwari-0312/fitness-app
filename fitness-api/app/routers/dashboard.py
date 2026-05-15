from datetime import date, datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.activity_log import ActivityLog
from app.models.food_item import FoodItem
from app.models.food_log import FoodLog
from app.models.user import User
from app.schemas.dashboard import DashboardOut, WeeklyTrendDay
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


@router.get("/weekly-trend", response_model=list[WeeklyTrendDay])
def get_weekly_trend(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    today = datetime.utcnow().date()
    start = today - timedelta(days=6)

    food_rows = (
        db.query(
            FoodLog.log_date,
            func.sum(FoodItem.calories_per_100g * FoodLog.quantity_grams / 100),
        )
        .join(FoodItem, FoodLog.food_item_id == FoodItem.id)
        .filter(FoodLog.user_id == current_user.id, FoodLog.log_date >= start)
        .group_by(FoodLog.log_date)
        .all()
    )
    consumed_by_date = {row[0]: row[1] for row in food_rows}

    activity_rows = (
        db.query(ActivityLog.log_date, func.sum(ActivityLog.calories_burned))
        .filter(ActivityLog.user_id == current_user.id, ActivityLog.log_date >= start)
        .group_by(ActivityLog.log_date)
        .all()
    )
    burned_by_date = {row[0]: row[1] for row in activity_rows}

    result = []
    for i in range(7):
        d = start + timedelta(days=i)
        consumed = consumed_by_date.get(d, 0.0)
        burned = burned_by_date.get(d, 0.0)
        has_data = d in consumed_by_date or d in burned_by_date
        result.append(WeeklyTrendDay(
            log_date=d,
            net_calories=round(consumed - burned, 2),
            has_data=has_data,
        ))
    return result
