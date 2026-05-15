from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.water_log import WaterLog
from app.schemas.water import WaterLogCreate, WaterLogOut
from app.utils.dependencies import get_current_user

router = APIRouter(prefix="/api/v1", tags=["water"])


@router.post("/water-logs", response_model=WaterLogOut, status_code=status.HTTP_201_CREATED)
def create_water_log(
    payload: WaterLogCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    log = WaterLog(
        user_id=current_user.id,
        amount_ml=payload.amount_ml,
        log_date=payload.log_date,
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


@router.get("/water-logs", response_model=list[WaterLogOut])
def get_water_logs(
    log_date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(WaterLog).filter(WaterLog.user_id == current_user.id)
    if log_date:
        query = query.filter(WaterLog.log_date == log_date)
    return query.order_by(WaterLog.created_at).all()
