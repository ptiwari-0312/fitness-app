# Fitness App — Local Setup

React + FastAPI + PostgreSQL POC.

## Prerequisites
- Docker Desktop
- Python 3.11+
- Node.js 18+

## 5-Step Setup

### 1. Start the database
```bash
docker compose up -d
```
Starts PostgreSQL 15 on port 5432 (`fitnessdb` / `fitness` / `fitness123`).

### 2. Install API dependencies
```bash
cd fitness-api
python -m venv .venv
# Windows:  .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Run migrations and seed food items
```bash
# inside fitness-api/ with venv active
alembic upgrade head
python -m seeds.food_items
```

### 4. Start the API
```bash
# inside fitness-api/ with venv active
uvicorn app.main:app --reload
```
API runs at <http://localhost:8000>. Interactive docs at <http://localhost:8000/docs>.

### 5. Start the frontend
```bash
cd fitness-ui
npm install
npm run dev
```
UI runs at <http://localhost:5173>.
