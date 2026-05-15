from typing import Optional, Literal

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.user import UserOut, UserUpdate, BMROut
from app.services.bmr_service import calculate_bmr, calculate_tdee
from app.utils.dependencies import get_current_user

router = APIRouter(prefix="/api/v1/users", tags=["users"])


@router.get("/me", response_model=UserOut)
def get_profile(current_user: User = Depends(get_current_user)):
    return current_user


@router.put("/me", response_model=UserOut)
def update_profile(
    payload: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    for field, value in payload.model_dump(exclude_none=True).items():
        setattr(current_user, field, value)
    db.commit()
    db.refresh(current_user)
    return current_user


@router.get("/me/bmr", response_model=BMROut)
def get_bmr(current_user: User = Depends(get_current_user)):
    bmr = calculate_bmr(current_user.weight_kg, current_user.height_cm, current_user.age, current_user.gender)
    tdee = calculate_tdee(bmr, current_user.activity_level)
    return BMROut(bmr=round(bmr, 2), tdee=round(tdee, 2))
