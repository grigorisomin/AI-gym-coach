from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

from db.database import create_db_and_tables
from routers import garmin, calendar, coach


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(
    title="AI Gym Coach API",
    description="Local backend for syncing Garmin + Google Calendar data and AI coaching.",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(garmin.router)
app.include_router(calendar.router)
app.include_router(coach.router)


@app.get("/health")
def health():
    return {"status": "ok"}
