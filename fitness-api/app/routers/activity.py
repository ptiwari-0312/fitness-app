from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.activity_log import ActivityLog
from app.models.user import User
from app.schemas.activity import ActivityLogCreate, ActivityLogOut
from app.services.bmr_service import calories_burned_from_steps
from app.utils.dependencies import get_current_user

router = APIRouter(prefix="/api/v1", tags=["activity"])


@router.post("/activity-logs", response_model=ActivityLogOut, status_code=201)
def create_activity_log(
    payload: ActivityLogCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    burned = calories_burned_from_steps(payload.steps_count, current_user.weight_kg)
    log = ActivityLog(
        user_id=current_user.id,
        steps_count=payload.steps_count,
        calories_burned=round(burned, 2),
        log_date=payload.log_date,
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


@router.get("/activity-logs", response_model=list[ActivityLogOut])
def get_activity_logs(
    log_date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(ActivityLog).filter(ActivityLog.user_id == current_user.id)
    if log_date:
        query = query.filter(ActivityLog.log_date == log_date)
    return query.order_by(ActivityLog.created_at).all()
