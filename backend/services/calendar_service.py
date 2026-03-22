import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from sqlmodel import Session, select

from db.database import CalendarEvent

SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]


def _get_service():
    credentials_path = os.getenv("GOOGLE_CREDENTIALS_PATH", "credentials.json")
    token_path = os.getenv("GOOGLE_TOKEN_PATH", "token.json")

    creds: Optional[Credentials] = None

    if Path(token_path).exists():
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not Path(credentials_path).exists():
                raise FileNotFoundError(
                    f"Google credentials file not found at '{credentials_path}'. "
                    "Download it from Google Cloud Console and set GOOGLE_CREDENTIALS_PATH in .env"
                )
            flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
            creds = flow.run_local_server(port=0)

        with open(token_path, "w") as f:
            f.write(creds.to_json())

    return build("calendar", "v3", credentials=creds)


def sync_events(session: Session, days_ahead: int = 14, days_behind: int = 7) -> dict:
    service = _get_service()

    now = datetime.now(timezone.utc)
    time_min = (now - timedelta(days=days_behind)).isoformat()
    time_max = (now + timedelta(days=days_ahead)).isoformat()

    calendars_result = service.calendarList().list().execute()
    calendars = calendars_result.get("items", [])

    created = 0
    updated = 0

    for calendar in calendars:
        cal_id = calendar["id"]
        cal_name = calendar.get("summary", cal_id)

        events_result = (
            service.events()
            .list(
                calendarId=cal_id,
                timeMin=time_min,
                timeMax=time_max,
                singleEvents=True,
                orderBy="startTime",
                maxResults=100,
            )
            .execute()
        )

        for event in events_result.get("items", []):
            google_id = event["id"]
            summary = event.get("summary", "(No title)")
            description = event.get("description")

            start = event.get("start", {})
            end = event.get("end", {})

            is_all_day = "date" in start and "dateTime" not in start

            if is_all_day:
                start_time = datetime.fromisoformat(start["date"])
                end_time = datetime.fromisoformat(end["date"]) if "date" in end else None
            else:
                start_time = datetime.fromisoformat(
                    start["dateTime"].replace("Z", "+00:00")
                )
                end_time = (
                    datetime.fromisoformat(end["dateTime"].replace("Z", "+00:00"))
                    if "dateTime" in end
                    else None
                )

            existing = session.exec(
                select(CalendarEvent).where(CalendarEvent.google_id == google_id)
            ).first()

            event_data = dict(
                google_id=google_id,
                summary=summary,
                description=description,
                start_time=start_time,
                end_time=end_time,
                is_all_day=is_all_day,
                calendar_name=cal_name,
                synced_at=datetime.utcnow(),
            )

            if existing:
                for k, v in event_data.items():
                    setattr(existing, k, v)
                updated += 1
            else:
                session.add(CalendarEvent(**event_data))
                created += 1

    session.commit()
    return {"created": created, "updated": updated}


def get_upcoming_events(session: Session, days: int = 7) -> list[CalendarEvent]:
    now = datetime.utcnow()
    cutoff = now + timedelta(days=days)
    return session.exec(
        select(CalendarEvent)
        .where(CalendarEvent.start_time >= now)
        .where(CalendarEvent.start_time <= cutoff)
        .order_by(CalendarEvent.start_time)
    ).all()
