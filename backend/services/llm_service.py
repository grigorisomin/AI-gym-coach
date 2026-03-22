import os
from datetime import datetime, timedelta
from typing import Generator

import ollama
from sqlmodel import Session

from db.database import Activity, SleepRecord, CalendarEvent, CoachMessage
from sqlmodel import select


def _format_duration(seconds: float) -> str:
    minutes = int(seconds // 60)
    if minutes >= 60:
        return f"{minutes // 60}h {minutes % 60}m"
    return f"{minutes}m"


def _build_context(session: Session) -> str:
    now = datetime.utcnow()
    week_ago = now - timedelta(days=7)
    two_weeks_ahead = now + timedelta(days=14)

    activities = session.exec(
        select(Activity)
        .where(Activity.start_time >= week_ago)
        .order_by(Activity.start_time.desc())
    ).all()

    sleep_records = session.exec(
        select(SleepRecord)
        .where(SleepRecord.date >= week_ago.date().isoformat())
        .order_by(SleepRecord.date.desc())
    ).all()

    upcoming_events = session.exec(
        select(CalendarEvent)
        .where(CalendarEvent.start_time >= now)
        .where(CalendarEvent.start_time <= two_weeks_ahead)
        .order_by(CalendarEvent.start_time)
    ).all()

    lines = [f"Today is {now.strftime('%A, %B %d, %Y')}.\n"]

    if activities:
        lines.append("## Recent Workouts (last 7 days)")
        for a in activities:
            parts = [
                f"- {a.start_time.strftime('%a %b %d')}: {a.name} ({a.activity_type})",
                f"duration {_format_duration(a.duration_seconds)}",
            ]
            if a.distance_meters:
                km = a.distance_meters / 1000
                parts.append(f"distance {km:.1f}km")
            if a.avg_hr:
                parts.append(f"avg HR {a.avg_hr}bpm")
            if a.calories:
                parts.append(f"{a.calories}kcal")
            if a.training_load:
                parts.append(f"training load {a.training_load:.0f}")
            lines.append(", ".join(parts))
        lines.append("")

    if sleep_records:
        lines.append("## Recent Sleep (last 7 days)")
        for s in sleep_records:
            parts = [f"- {s.date}:"]
            if s.duration_seconds:
                parts.append(f"slept {_format_duration(s.duration_seconds)}")
            if s.sleep_score:
                parts.append(f"sleep score {s.sleep_score}/100")
            if s.hrv_nightly:
                parts.append(f"HRV {s.hrv_nightly:.0f}ms")
            lines.append(" ".join(parts))
        lines.append("")

    if upcoming_events:
        lines.append("## Upcoming Calendar Events (next 14 days)")
        for e in upcoming_events:
            date_str = e.start_time.strftime("%a %b %d %H:%M") if not e.is_all_day else e.start_time.strftime("%a %b %d (all day)")
            lines.append(f"- {date_str}: {e.summary}")
        lines.append("")

    if not activities and not sleep_records:
        lines.append("No recent workout or sleep data synced yet. Suggest the user sync their Garmin data.")

    return "\n".join(lines)


SYSTEM_PROMPT = """You are an expert personal trainer and sports coach AI assistant. 
You have access to the user's recent workout history, sleep data, and calendar from their Garmin device and Google Calendar.

Use this data to give personalized, evidence-based advice. Be concise and actionable.
Consider training load, recovery metrics (HRV, sleep score), and upcoming schedule when making recommendations.

Always ground your advice in the user's actual data when it's available. If data is missing or not yet synced, say so clearly."""


def build_chat_messages(session: Session, user_message: str) -> list[dict]:
    context = _build_context(session)

    history = session.exec(
        select(CoachMessage)
        .order_by(CoachMessage.created_at.desc())
        .limit(20)
    ).all()
    history = list(reversed(history))

    messages = [
        {
            "role": "system",
            "content": f"{SYSTEM_PROMPT}\n\n## Your Current User Data\n{context}",
        }
    ]

    for msg in history:
        messages.append({"role": msg.role, "content": msg.content})

    messages.append({"role": "user", "content": user_message})
    return messages


def chat(session: Session, user_message: str) -> str:
    model = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
    base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

    messages = build_chat_messages(session, user_message)

    client = ollama.Client(host=base_url)
    response = client.chat(model=model, messages=messages)
    reply = response["message"]["content"]

    session.add(CoachMessage(role="user", content=user_message))
    session.add(CoachMessage(role="assistant", content=reply))
    session.commit()

    return reply


def chat_stream(session: Session, user_message: str) -> Generator[str, None, None]:
    model = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
    base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

    messages = build_chat_messages(session, user_message)

    client = ollama.Client(host=base_url)

    full_reply = []
    for chunk in client.chat(model=model, messages=messages, stream=True):
        token = chunk["message"]["content"]
        full_reply.append(token)
        yield token

    reply = "".join(full_reply)
    session.add(CoachMessage(role="user", content=user_message))
    session.add(CoachMessage(role="assistant", content=reply))
    session.commit()


def clear_history(session: Session) -> int:
    messages = session.exec(select(CoachMessage)).all()
    count = len(messages)
    for m in messages:
        session.delete(m)
    session.commit()
    return count
