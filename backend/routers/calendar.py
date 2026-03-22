from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from db.database import get_session, CalendarEvent
from services import calendar_service

router = APIRouter(prefix="/calendar", tags=["calendar"])

SessionDep = Annotated[Session, Depends(get_session)]


@router.post("/sync")
def sync_calendar(session: SessionDep):
    """Sync events from all Google Calendars (7 days behind, 14 days ahead)."""
    try:
        result = calendar_service.sync_events(session)
        return {"status": "ok", **result}
    except FileNotFoundError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Calendar sync failed: {str(e)}")


@router.get("/events", response_model=list[CalendarEvent])
def get_events(session: SessionDep, days: int = 14):
    """Return upcoming calendar events for the next N days (default 14)."""
    return calendar_service.get_upcoming_events(session, days=days)
