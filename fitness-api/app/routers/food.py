from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.food_item import FoodItem
from app.models.food_log import FoodLog
from app.models.user import User
from app.schemas.food import FoodItemOut, FoodLogCreate, FoodLogOut
from app.utils.dependencies import get_current_user

router = APIRouter(prefix="/api/v1", tags=["food"])


@router.get("/food-items", response_model=list[FoodItemOut])
def list_food_items(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return db.query(FoodItem).order_by(FoodItem.name).all()


@router.post("/food-logs", response_model=FoodLogOut, status_code=status.HTTP_201_CREATED)
def create_food_log(
    payload: FoodLogCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not db.query(FoodItem).filter(FoodItem.id == payload.food_item_id).first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Food item not found")

    log = FoodLog(
        user_id=current_user.id,
        food_item_id=payload.food_item_id,
        quantity_grams=payload.quantity_grams,
        log_date=payload.log_date,
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


@router.get("/food-logs", response_model=list[FoodLogOut])
def get_food_logs(
    log_date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(FoodLog).filter(FoodLog.user_id == current_user.id)
    if log_date:
        query = query.filter(FoodLog.log_date == log_date)
    return query.order_by(FoodLog.created_at).all()


@router.delete("/food-logs/{log_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_food_log(
    log_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    log = db.query(FoodLog).filter(FoodLog.id == log_id, FoodLog.user_id == current_user.id).first()
    if not log:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Log not found")
    db.delete(log)
    db.commit()
