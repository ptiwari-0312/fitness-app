# Fitness MVP — Project context for Claude Code

## What we're building
A fitness web app POC with React frontend, Python FastAPI backend, PostgreSQL DB.

## Tech stack
- Frontend: React 18 + Vite + TailwindCSS + Zustand + Axios + React Router v6
- Backend: FastAPI + SQLAlchemy 2.0 + Alembic + python-jose + passlib
- Database: PostgreSQL 15 (local via Docker)
- Server: Uvicorn (ASGI)

## Folder layout
- /fitness-api   → Python FastAPI backend
- /fitness-ui    → React frontend

## Database tables
- users          (id, name, email, password_hash, age, gender, weight_kg, height_cm, activity_level, created_at)
- food_items     (id, name, calories_per_100g, protein_per_100g, carb_per_100g, fat_per_100g)  ← seed data, read-only
- food_logs      (id, user_id FK, food_item_id FK, quantity_grams, log_date, created_at)
- activity_logs  (id, user_id FK, steps_count, calories_burned, log_date, created_at)

## Core formulas (implement in app/services/bmr_service.py)
- BMR male:   (10 × weight_kg) + (6.25 × height_cm) − (5 × age) + 5
- BMR female: (10 × weight_kg) + (6.25 × height_cm) − (5 × age) − 161
- TDEE = BMR × activity_multiplier (sedentary=1.2, light=1.375, moderate=1.55, active=1.725, very_active=1.9)
- Calories burned from steps = steps × 0.0005 × weight_kg
- Net calories = calories_consumed − calories_burned

## API prefix
All routes: /api/v1/

## Auth
JWT with 24h expiry. Protected routes use get_current_user() FastAPI dependency.

## Seed food items (12 items)
Chicken breast, Brown rice, Whole egg, Banana, Rolled oats, Paneer,
Whole wheat roti, Cooked dal (masoor), Apple, Full-fat milk, Peanut butter, Sweet potato

## MVP scope — do not add beyond this
No email verification, no refresh tokens, no custom food items, no chart libraries.
Keep it simple and demo-ready.