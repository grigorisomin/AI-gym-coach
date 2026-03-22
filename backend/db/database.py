from pathlib import Path
from typing import Optional
from datetime import datetime

from sqlmodel import Field, SQLModel, Session, create_engine, select

DB_PATH = Path(__file__).parent.parent / "gym_coach.db"
DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(DATABASE_URL, echo=False)


# --- Models ---

class Activity(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    garmin_id: str = Field(index=True, unique=True)
    name: str
    activity_type: str
    start_time: datetime
    duration_seconds: float
    distance_meters: Optional[float] = None
    avg_hr: Optional[int] = None
    max_hr: Optional[int] = None
    calories: Optional[int] = None
    avg_speed: Optional[float] = None
    elevation_gain: Optional[float] = None
    hrv_status: Optional[str] = None
    aerobic_training_effect: Optional[float] = None
    anaerobic_training_effect: Optional[float] = None
    training_load: Optional[float] = None
    raw_json: Optional[str] = None
    synced_at: datetime = Field(default_factory=datetime.utcnow)


class SleepRecord(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    date: str = Field(index=True, unique=True)  # YYYY-MM-DD
    duration_seconds: Optional[float] = None
    deep_sleep_seconds: Optional[float] = None
    light_sleep_seconds: Optional[float] = None
    rem_sleep_seconds: Optional[float] = None
    awake_seconds: Optional[float] = None
    sleep_score: Optional[int] = None
    hrv_nightly: Optional[float] = None
    raw_json: Optional[str] = None
    synced_at: datetime = Field(default_factory=datetime.utcnow)


class CalendarEvent(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    google_id: str = Field(index=True, unique=True)
    summary: str
    description: Optional[str] = None
    start_time: datetime
    end_time: Optional[datetime] = None
    is_all_day: bool = False
    calendar_name: Optional[str] = None
    synced_at: datetime = Field(default_factory=datetime.utcnow)


class CoachMessage(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    role: str  # "user" or "assistant"
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
