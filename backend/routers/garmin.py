import os
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from db.database import get_session, Activity, SleepRecord
from services import garmin_service

router = APIRouter(prefix="/garmin", tags=["garmin"])

SessionDep = Annotated[Session, Depends(get_session)]


@router.post("/sync")
def sync_garmin(session: SessionDep):
    """Sync recent activities and sleep data from Garmin Connect."""
    days = int(os.getenv("GARMIN_SYNC_DAYS", "30"))
    try:
        activity_result = garmin_service.sync_activities(session, days=days)
        sleep_result = garmin_service.sync_sleep(session, days=days)
        return {
            "status": "ok",
            "activities": activity_result,
            "sleep": sleep_result,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Garmin sync failed: {str(e)}")


@router.get("/activities", response_model=list[Activity])
def get_activities(session: SessionDep, days: int = 7):
    """Return activities from the last N days (default 7)."""
    return garmin_service.get_activities(session, days=days)


@router.get("/sleep", response_model=list[SleepRecord])
def get_sleep(session: SessionDep, days: int = 7):
    """Return sleep records from the last N days (default 7)."""
    return garmin_service.get_sleep_records(session, days=days)
