from sqlalchemy import Column, Float, Integer, String

from app.database import Base


class FoodItem(Base):
    __tablename__ = "food_items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    calories_per_100g = Column(Float, nullable=False)
    protein_per_100g = Column(Float, nullable=False)
    carb_per_100g = Column(Float, nullable=False)
    fat_per_100g = Column(Float, nullable=False)
