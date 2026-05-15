# FitnessApp — System Design Document

**Version:** 1.0  
**Type:** MVP / POC  
**Stack:** React · Python FastAPI · PostgreSQL  

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Architecture Overview](#2-architecture-overview)
3. [Tech Stack](#3-tech-stack)
4. [Folder Structure](#4-folder-structure)
5. [Database Design](#5-database-design)
6. [API Design](#6-api-design)
7. [Business Logic & Formulas](#7-business-logic--formulas)
8. [Seed Data](#8-seed-data)
9. [Infrastructure & Local Setup](#9-infrastructure--local-setup)
10. [Claude Code Integration](#10-claude-code-integration)
11. [MVP Scope Boundaries](#11-mvp-scope-boundaries)

---

## 1. Project Overview

FitnessApp is a web-based fitness tracking MVP designed as a proof-of-concept demonstration. It enables users to:

- Enrol and manage their profile (age, weight, height, activity level)
- Calculate their **BMR (Basal Metabolic Rate)** and **TDEE (Total Daily Energy Expenditure)**
- Track **daily calorie intake** by logging food consumed in grams from a curated list
- Track **calories burned** by entering daily step count
- View a **dashboard** showing net calorie balance, surplus, or deficit for the day

---

## 2. Architecture Overview

The application follows a classic **three-tier architecture**:

```
┌─────────────────────────────────────────────────────┐
│                   BROWSER (Client)                  │
│  React SPA · Vite · TailwindCSS · Zustand · Axios   │
│  Auth Pages · Dashboard · Food Log · Activity Log   │
└──────────────────────┬──────────────────────────────┘
                       │  REST / JSON  (JWT Bearer)
┌──────────────────────▼──────────────────────────────┐
│              PYTHON FASTAPI BACKEND                 │
│                   (Uvicorn ASGI)                    │
│                                                     │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌───────┐  │
│  │   Auth   │ │  Users   │ │   Food   │ │Activity│ │
│  │  module  │ │  + BMR   │ │  module  │ │module │  │
│  └──────────┘ └──────────┘ └──────────┘ └───────┘  │
│                    ┌──────────────┐                 │
│                    │  Dashboard   │                 │
│                    │   summary    │                 │
│                    └──────────────┘                 │
└──────────────────────┬──────────────────────────────┘
                       │  SQLAlchemy ORM
┌──────────────────────▼──────────────────────────────┐
│              POSTGRESQL 15 DATABASE                 │
│                                                     │
│   users · food_items · food_logs · activity_logs   │
└─────────────────────────────────────────────────────┘
```

### Key design decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Frontend state | Zustand | Lightweight; perfect for JWT token + user object |
| HTTP client | Axios | Interceptors enable automatic JWT header injection |
| ORM | SQLAlchemy 2.0 | Best-in-class Python ORM; Alembic handles migrations |
| Auth | JWT (24h expiry) | Stateless; no session store needed for MVP |
| DB | PostgreSQL 15 | Free, open source, runs locally via Docker |
| API docs | FastAPI auto Swagger | Zero-config interactive docs at `/docs` |

---

## 3. Tech Stack

| Layer | Technology | Version |
|-------|-----------|---------|
| Frontend framework | React | 18.x |
| Build tool | Vite | Latest |
| Styling | TailwindCSS | 3.x |
| Client state | Zustand | Latest |
| HTTP client | Axios | Latest |
| Routing | React Router | v6 |
| Backend framework | FastAPI | Latest |
| ASGI server | Uvicorn | Latest |
| ORM | SQLAlchemy | 2.0 |
| Migrations | Alembic | Latest |
| Auth - JWT | python-jose[cryptography] | Latest |
| Auth - hashing | passlib[bcrypt] | Latest |
| Config | pydantic-settings | Latest |
| Database | PostgreSQL | 15 |

### Python `requirements.txt`

```
fastapi
uvicorn[standard]
sqlalchemy
alembic
psycopg2-binary
python-jose[cryptography]
passlib[bcrypt]
pydantic-settings
python-multipart
```

---

## 4. Folder Structure

```
fitness-app/
├── docker-compose.yml          ← PostgreSQL 15 service
├── CLAUDE.md                   ← Claude Code context file
├── README.md
│
├── fitness-api/                ← Python FastAPI backend
│   ├── .env                    ← DATABASE_URL, SECRET_KEY, ALGORITHM
│   ├── requirements.txt
│   ├── alembic/                ← DB migration scripts
│   │   └── versions/
│   ├── seeds/
│   │   └── food_items.py       ← Seed script: 12 food items
│   └── app/
│       ├── main.py             ← FastAPI app, CORS, router registration
│       ├── config.py           ← Settings via pydantic-settings
│       ├── database.py         ← SQLAlchemy engine + session factory
│       ├── models/
│       │   ├── user.py         ← ORM model: users table
│       │   ├── food.py         ← ORM models: food_items + food_logs
│       │   └── activity.py     ← ORM model: activity_logs
│       ├── schemas/
│       │   ├── user.py         ← Pydantic request/response schemas
│       │   ├── food.py
│       │   └── activity.py
│       ├── routers/
│       │   ├── auth.py         ← /api/v1/auth/*
│       │   ├── users.py        ← /api/v1/users/*
│       │   ├── food.py         ← /api/v1/food-items, /food-logs
│       │   ├── activity.py     ← /api/v1/activity-logs
│       │   └── dashboard.py    ← /api/v1/dashboard/summary
│       ├── services/
│       │   ├── auth_service.py     ← hash, verify, create_access_token
│       │   ├── bmr_service.py      ← BMR, TDEE, step-calorie formulas
│       │   └── calorie_service.py  ← Aggregate daily totals
│       └── utils/
│           └── dependencies.py     ← get_current_user() FastAPI dependency
│
└── fitness-ui/                 ← React frontend
    ├── package.json
    ├── vite.config.js
    ├── tailwind.config.js
    └── src/
        ├── App.jsx             ← Routes + ProtectedRoute wrapper
        ├── main.jsx
        ├── api/
        │   └── client.js       ← Axios instance with JWT interceptor
        ├── pages/
        │   ├── Login.jsx
        │   ├── Register.jsx
        │   ├── Dashboard.jsx   ← BMR, TDEE, net calorie summary cards
        │   ├── FoodLog.jsx     ← Dropdown + grams input + submit
        │   └── ActivityLog.jsx ← Steps input + submit
        ├── components/
        │   ├── NavBar.jsx
        │   ├── BMRCard.jsx
        │   ├── CalorieSummary.jsx
        │   └── FoodSearch.jsx
        ├── store/
        │   └── authStore.js    ← Zustand: JWT token + user object
        └── utils/
            └── formulas.js     ← Client-side BMR for instant preview
```

---

## 5. Database Design

### Entity Relationship Overview

```
users ──< food_logs >── food_items
users ──< activity_logs
```

### Table: `users`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, default gen_random_uuid() | Primary key |
| name | VARCHAR(100) | NOT NULL | Full name |
| email | VARCHAR(255) | NOT NULL, UNIQUE | Login email |
| password_hash | VARCHAR(255) | NOT NULL | bcrypt hash |
| age | INTEGER | NOT NULL | Age in years |
| gender | VARCHAR(10) | NOT NULL | 'male' or 'female' |
| weight_kg | FLOAT | NOT NULL | Weight in kilograms |
| height_cm | FLOAT | NOT NULL | Height in centimetres |
| activity_level | VARCHAR(20) | NOT NULL | sedentary / light / moderate / active / very_active |
| created_at | TIMESTAMP | NOT NULL, default now() | Record creation time |

### Table: `food_items` *(seed data — read-only at runtime)*

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PK | Primary key |
| name | VARCHAR(100) | NOT NULL, UNIQUE | Food name |
| calories_per_100g | FLOAT | NOT NULL | kcal per 100g |
| protein_per_100g | FLOAT | NOT NULL | grams protein per 100g |
| carb_per_100g | FLOAT | NOT NULL | grams carbohydrate per 100g |
| fat_per_100g | FLOAT | NOT NULL | grams fat per 100g |

### Table: `food_logs`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, default gen_random_uuid() | Primary key |
| user_id | UUID | NOT NULL, FK → users.id | Owning user |
| food_item_id | INTEGER | NOT NULL, FK → food_items.id | Food reference |
| quantity_grams | FLOAT | NOT NULL | Quantity consumed in grams |
| log_date | DATE | NOT NULL | Date of consumption |
| created_at | TIMESTAMP | NOT NULL, default now() | Record creation time |

### Table: `activity_logs`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, default gen_random_uuid() | Primary key |
| user_id | UUID | NOT NULL, FK → users.id | Owning user |
| steps_count | INTEGER | NOT NULL | Steps taken that day |
| calories_burned | FLOAT | NOT NULL | Computed from steps × formula |
| log_date | DATE | NOT NULL | Date of activity |
| created_at | TIMESTAMP | NOT NULL, default now() | Record creation time |

---

## 6. API Design

All endpoints are prefixed with `/api/v1/`.  
Protected routes require header: `Authorization: Bearer <JWT_TOKEN>`

### Auth module

| Method | Endpoint | Auth | Request body | Response |
|--------|----------|------|-------------|----------|
| POST | `/auth/register` | Public | `{name, email, password, age, gender, weight_kg, height_cm, activity_level}` | `{access_token, token_type, user}` |
| POST | `/auth/login` | Public | `{email, password}` | `{access_token, token_type, user}` |
| GET | `/auth/me` | Protected | — | User profile object |

### Users module

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/users/{id}` | Protected | Fetch full user profile |
| PUT | `/users/{id}` | Protected | Update weight, height, age, activity_level |
| GET | `/users/{id}/bmr` | Protected | Returns `{bmr, tdee, activity_level, multiplier}` |

### Food module

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/food-items` | Protected | Return all 12 seeded food items |
| POST | `/food-logs` | Protected | Log food: `{food_item_id, quantity_grams, log_date}` |
| GET | `/food-logs?date=YYYY-MM-DD` | Protected | All food logs for authenticated user on that date |
| DELETE | `/food-logs/{log_id}` | Protected | Remove a specific food log entry |

### Activity module

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/activity-logs` | Protected | Submit `{steps_count, log_date}` — backend computes `calories_burned` |
| GET | `/activity-logs?date=YYYY-MM-DD` | Protected | Fetch activity log for a date |

### Dashboard module

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/dashboard/summary?date=YYYY-MM-DD` | Protected | Full daily summary |

**Dashboard response payload:**

```json
{
  "date": "2025-05-14",
  "bmr": 1680.0,
  "tdee": 2310.0,
  "total_calories_consumed": 1850.5,
  "total_calories_burned": 350.0,
  "net_calories": 1500.5,
  "surplus_deficit": -809.5,
  "status": "deficit"
}
```

---

## 7. Business Logic & Formulas

All formulas are implemented in `app/services/bmr_service.py`.

### BMR — Mifflin-St Jeor Equation

Most accurate general-population formula. Preferred over Harris-Benedict for MVP.

```
Male:   BMR = (10 × weight_kg) + (6.25 × height_cm) − (5 × age) + 5
Female: BMR = (10 × weight_kg) + (6.25 × height_cm) − (5 × age) − 161
```

**Example (Male, 25yr, 75kg, 175cm):**  
`BMR = (10×75) + (6.25×175) − (5×25) + 5 = 750 + 1093.75 − 125 + 5 = 1723.75 kcal/day`

### TDEE — Total Daily Energy Expenditure

```
TDEE = BMR × activity_multiplier

Activity multipliers:
  sedentary   → 1.200   (desk job, little exercise)
  light       → 1.375   (light exercise 1–3 days/week)
  moderate    → 1.550   (moderate exercise 3–5 days/week)
  active      → 1.725   (hard exercise 6–7 days/week)
  very_active → 1.900   (physical job + hard exercise)
```

### Calories Burned from Steps

Weight-adjusted formula (more accurate than flat rate per step):

```
calories_burned = steps_count × 0.0005 × weight_kg
```

**Example (70kg user, 10,000 steps):**  
`calories_burned = 10000 × 0.0005 × 70 = 350 kcal` ✓ matches real-world estimates

### Daily Calorie Calculations

```python
# Calories consumed from food logs
calories_consumed = sum(
    (food_item.calories_per_100g * log.quantity_grams) / 100
    for log in day_food_logs
)

# Net calories (what was actually consumed minus burned)
net_calories = calories_consumed - calories_burned

# Surplus or deficit against TDEE
surplus_deficit = net_calories - tdee
# Negative = calorie deficit (weight loss direction)
# Positive = calorie surplus (weight gain direction)
```

---

## 8. Seed Data

Loaded via `seeds/food_items.py` after running migrations. These 12 items cover common Indian and international foods suitable for POC demonstration.

| # | Food Item | Cal/100g | Protein/100g | Carbs/100g | Fat/100g |
|---|-----------|----------|--------------|------------|----------|
| 1 | Chicken breast (cooked) | 165 kcal | 31.0g | 0.0g | 3.6g |
| 2 | Brown rice (cooked) | 216 kcal | 5.0g | 45.0g | 1.8g |
| 3 | Whole egg | 155 kcal | 13.0g | 1.1g | 11.0g |
| 4 | Banana | 89 kcal | 1.1g | 23.0g | 0.3g |
| 5 | Rolled oats | 389 kcal | 17.0g | 66.0g | 7.0g |
| 6 | Paneer | 265 kcal | 18.0g | 3.4g | 20.0g |
| 7 | Whole wheat roti | 297 kcal | 11.0g | 61.0g | 1.6g |
| 8 | Cooked dal (masoor) | 116 kcal | 9.0g | 20.0g | 0.4g |
| 9 | Apple | 52 kcal | 0.3g | 14.0g | 0.2g |
| 10 | Full-fat milk | 61 kcal | 3.2g | 4.8g | 3.3g |
| 11 | Peanut butter | 588 kcal | 25.0g | 20.0g | 50.0g |
| 12 | Sweet potato (cooked) | 86 kcal | 1.6g | 20.0g | 0.1g |

---

## 9. Infrastructure & Local Setup

### Docker Compose (`docker-compose.yml`)

```yaml
version: '3.8'

services:
  db:
    image: postgres:15
    container_name: fitness-db
    environment:
      POSTGRES_DB: fitnessdb
      POSTGRES_USER: fitness
      POSTGRES_PASSWORD: fitness123
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

### Environment File (`fitness-api/.env`)

```env
DATABASE_URL=postgresql://fitness:fitness123@localhost:5432/fitnessdb
SECRET_KEY=your-strong-random-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
```

### Local Setup — 5 Steps

```bash
# Step 1: Start PostgreSQL via Docker
docker-compose up -d

# Step 2: Set up and run the backend
cd fitness-api
pip install -r requirements.txt
alembic upgrade head             # run all migrations
python seeds/food_items.py       # load 12 seed food items
uvicorn app.main:app --reload    # starts on http://localhost:8000

# Step 3: Set up and run the frontend
cd ../fitness-ui
npm install
npm run dev                      # starts on http://localhost:5173

# Step 4: Verify backend
# Open http://localhost:8000/docs  →  Swagger UI with all routes

# Step 5: Open the app
# Open http://localhost:5173  →  Register → Log food → Log steps → Dashboard
```

### Verification Checkpoints

```bash
# Confirm DB tables exist
docker exec -it fitness-db psql -U fitness -d fitnessdb -c "\dt"

# Confirm seed data loaded
docker exec -it fitness-db psql -U fitness -d fitnessdb \
  -c "SELECT name, calories_per_100g FROM food_items;"
# → Should return 12 rows

# Health check
curl http://localhost:8000/api/v1/auth/me
# → Should return 401 Unauthorized (confirming auth is wired up)
```

---

## 10. Claude Code Integration

### CLAUDE.md (place in project root)

This file gives Claude Code persistent project context across every session:

```markdown
# FitnessApp — Claude Code context

Tech stack: React 18 + Vite + TailwindCSS + Zustand | FastAPI + SQLAlchemy 2.0 + Alembic | PostgreSQL 15

Folder layout:
  /fitness-api  → Python backend
  /fitness-ui   → React frontend

All API routes prefixed: /api/v1/
Auth: JWT 24h expiry via get_current_user() dependency in utils/dependencies.py
Business logic: bmr_service.py (BMR, TDEE, step-calorie formulas)

See SYSTEM_DESIGN.md for full schema, formulas, and API reference.
```

### Recommended Claude Code Prompt Sequence

| Phase | Prompt focus |
|-------|-------------|
| 1 | Scaffold `fitness-api` structure + `requirements.txt` |
| 2 | SQLAlchemy models + Alembic migration + seed script |
| 3 | Auth: `auth_service.py` + JWT dependency + `/auth` router |
| 4 | BMR service + Users, Food, Activity, Dashboard routers |
| 5 | Scaffold `fitness-ui` + Axios client + Zustand auth store |
| 6 | Build React pages: Login, Register, Dashboard, FoodLog, ActivityLog |
| 7 | `docker-compose.yml` + `.env` + `README.md` |

---

## 11. MVP Scope Boundaries

### In scope

- User enrolment (register + login with JWT)
- Profile management (update weight, height, age, activity level)
- BMR and TDEE calculation and display
- Food log: select from 12 seeded items, enter grams, view daily total
- Activity log: enter step count, backend computes calories burned
- Dashboard: daily summary — BMR, TDEE, consumed, burned, net, surplus/deficit

### Out of scope (defer post-demo)

| Feature | Reason deferred |
|---------|----------------|
| Email verification / password reset | Requires email service infrastructure |
| Refresh token rotation | Over-engineered for 24h MVP demo |
| Custom / user-defined food items | Seed list covers demo adequately |
| Exercise types beyond steps | Step formula sufficient for POC |
| Charts and data visualisations | No chart library to keep UI simple |
| Multi-user admin / analytics | Beyond single-user MVP scope |
| Mobile app | Web-first for POC |

---

## Document History

| Version | Date | Change |
|---------|------|--------|
| 1.0 | 2025-05-14 | Initial system design — MVP POC |

---

*Generated from FitnessApp architecture session. Tech stack: React · FastAPI · PostgreSQL.*
