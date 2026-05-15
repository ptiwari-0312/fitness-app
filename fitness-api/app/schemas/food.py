from datetime import date, datetime

from pydantic import BaseModel


class FoodItemOut(BaseModel):
    id: int
    name: str
    calories_per_100g: float
    protein_per_100g: float
    carb_per_100g: float
    fat_per_100g: float

    model_config = {"from_attributes": True}


class FoodLogCreate(BaseModel):
    food_item_id: int
    quantity_grams: float
    log_date: date


class FoodLogOut(BaseModel):
    id: int
    food_item_id: int
    food_item: FoodItemOut
    quantity_grams: float
    log_date: date
    created_at: datetime

    model_config = {"from_attributes": True}
