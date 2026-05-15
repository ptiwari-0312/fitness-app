from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import activity, auth, dashboard, food, users, water

app = FastAPI(title="Fitness API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(food.router)
app.include_router(activity.router)
app.include_router(dashboard.router)
app.include_router(water.router)
