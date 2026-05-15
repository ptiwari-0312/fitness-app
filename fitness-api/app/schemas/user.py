from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    age: int
    gender: Literal["male", "female"]
    weight_kg: float
    height_cm: float
    activity_level: Literal["sedentary", "light", "moderate", "active", "very_active"]


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    name: str
    email: str
    age: int
    gender: str
    weight_kg: float
    height_cm: float
    activity_level: str
    created_at: datetime

    model_config = {"from_attributes": True}


class UserUpdate(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[Literal["male", "female"]] = None
    weight_kg: Optional[float] = None
    height_cm: Optional[float] = None
    activity_level: Optional[Literal["sedentary", "light", "moderate", "active", "very_active"]] = None


class BMROut(BaseModel):
    bmr: float
    tdee: float


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
