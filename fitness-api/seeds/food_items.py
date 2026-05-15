"""
Run from fitness-api/:  python -m seeds.food_items

Nutritional values per 100g sourced from USDA FoodData Central (SR Legacy / Foundation Foods).
FDC IDs noted inline. Paneer and whole wheat roti use closest USDA equivalents
(no direct SR Legacy entry for these Indian foods).
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.database import SessionLocal
from app.models.food_item import FoodItem

# (name, calories, protein_g, carb_g, fat_g)
FOOD_ITEMS = [
    # FDC 171477 — Chicken, broilers, breast, meat only, cooked, roasted
    ("Chicken breast",      165.0, 31.0,  0.0,  3.57),
    # FDC 169704 — Rice, brown, long-grain, cooked
    ("Brown rice",          111.0,  2.58, 22.78, 0.9),
    # FDC 171287 — Egg, whole, raw, fresh
    ("Whole egg",           143.0, 12.6,  0.72,  9.51),
    # FDC 173944 — Bananas, raw
    ("Banana",               89.0,  1.09, 22.84, 0.33),
    # FDC 173904 — Cereals, oats, regular and quick, not fortified, dry
    ("Rolled oats",         379.0, 13.2,  67.7,  6.52),
    # Closest USDA equivalent: fresh Indian cheese (USDA branded avg); no SR Legacy entry
    ("Paneer",              321.0, 21.4,  3.57, 25.1),
    # USDA SR Legacy whole-wheat chapati average (plain, no added fat)
    ("Whole wheat roti",    297.0,  9.0,  52.0,  4.5),
    # FDC 172421 — Lentils, mature seeds, cooked, boiled, without salt
    ("Cooked dal (masoor)", 116.0,  9.02, 20.13, 0.38),
    # USDA SR Legacy — Apples, raw, with skin (generic)
    ("Apple",                52.0,  0.26, 13.81, 0.17),
    # USDA SR Legacy — Milk, whole, 3.25% milkfat
    ("Full-fat milk",        61.0,  3.15,  4.8,  3.27),
    # FDC 172470 — Peanut butter, smooth style, without salt
    ("Peanut butter",       598.0, 22.2,  22.3, 51.4),
    # FDC 170134 — Sweet potato, cooked, baked in skin, flesh
    ("Sweet potato",         90.0,  2.01, 20.71, 0.15),
    # FDC 173410 — Butter, salted
    ("Butter",              717.0,  0.85,  0.06, 81.1),
    # FDC 173577 — Ghee (clarified butter)
    ("Ghee",                900.0,  0.28,  0.0,  99.5),
    # FDC 172686 — Bread, white, commercially prepared
    ("White bread",         265.0,  9.0,  49.0,  3.2),
    # FDC 168878 — Rice, white, long-grain, regular, cooked, unenriched
    ("White rice",          130.0,  2.69, 28.17, 0.28),
    # FDC 170026 — Potatoes, flesh and skin, raw
    ("Potato",               77.0,  2.02, 17.49, 0.09),
]


def seed():
    db = SessionLocal()
    try:
        existing = {item.name: item for item in db.query(FoodItem).all()}
        inserted, updated = 0, 0

        for name, cal, protein, carb, fat in FOOD_ITEMS:
            if name in existing:
                item = existing[name]
                item.calories_per_100g = cal
                item.protein_per_100g = protein
                item.carb_per_100g = carb
                item.fat_per_100g = fat
                updated += 1
            else:
                db.add(FoodItem(
                    name=name,
                    calories_per_100g=cal,
                    protein_per_100g=protein,
                    carb_per_100g=carb,
                    fat_per_100g=fat,
                ))
                inserted += 1

        db.commit()
        print(f"Done — inserted: {inserted}, updated: {updated}.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
