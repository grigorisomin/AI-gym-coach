import json
import os
from datetime import datetime, timedelta, date
from typing import Optional

from garminconnect import Garmin, GarminConnectConnectionError, GarminConnectAuthenticationError
from sqlmodel import Session, select

from db.database import Activity, SleepRecord


def _get_client() -> Garmin:
    email = os.getenv("GARMIN_EMAIL")
    password = os.getenv("GARMIN_PASSWORD")
    if not email or not password:
        raise ValueError("GARMIN_EMAIL and GARMIN_PASSWORD must be set in .env")
    client = Garmin(email, password)
    client.login()
    return client


def sync_activities(session: Session, days: int = 30) -> dict:
    client = _get_client()

    end_date = date.today()
    start_date = end_date - timedelta(days=days)

    raw_activities = client.get_activities_by_date(
        start_date.isoformat(), end_date.isoformat()
    )

    created = 0
    updated = 0

    for raw in raw_activities:
        garmin_id = str(raw.get("activityId", ""))
        if not garmin_id:
            continue

        start_str = raw.get("startTimeLocal") or raw.get("startTimeGMT", "")
        try:
            start_time = datetime.fromisoformat(start_str.replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            continue

        existing = session.exec(
            select(Activity).where(Activity.garmin_id == garmin_id)
        ).first()

        activity_data = dict(
            garmin_id=garmin_id,
            name=raw.get("activityName", "Unknown"),
            activity_type=raw.get("activityType", {}).get("typeKey", "unknown"),
            start_time=start_time,
            duration_seconds=raw.get("duration", 0.0),
            distance_meters=raw.get("distance"),
            avg_hr=raw.get("averageHR"),
            max_hr=raw.get("maxHR"),
            calories=raw.get("calories"),
            avg_speed=raw.get("averageSpeed"),
            elevation_gain=raw.get("elevationGain"),
            aerobic_training_effect=raw.get("aerobicTrainingEffect"),
            anaerobic_training_effect=raw.get("anaerobicTrainingEffect"),
            training_load=raw.get("activityTrainingLoad"),
            raw_json=json.dumps(raw),
            synced_at=datetime.utcnow(),
        )

        if existing:
            for k, v in activity_data.items():
                setattr(existing, k, v)
            updated += 1
        else:
            session.add(Activity(**activity_data))
            created += 1

    session.commit()
    return {"created": created, "updated": updated, "total": len(raw_activities)}


def sync_sleep(session: Session, days: int = 30) -> dict:
    client = _get_client()

    created = 0
    updated = 0

    for i in range(days):
        day = date.today() - timedelta(days=i)
        day_str = day.isoformat()

        try:
            raw = client.get_sleep_data(day_str)
        except Exception:
            continue

        daily = raw.get("dailySleepDTO", {})
        if not daily:
            continue

        existing = session.exec(
            select(SleepRecord).where(SleepRecord.date == day_str)
        ).first()

        sleep_data = dict(
            date=day_str,
            duration_seconds=daily.get("sleepTimeSeconds"),
            deep_sleep_seconds=daily.get("deepSleepSeconds"),
            light_sleep_seconds=daily.get("lightSleepSeconds"),
            rem_sleep_seconds=daily.get("remSleepSeconds"),
            awake_seconds=daily.get("awakeSleepSeconds"),
            sleep_score=daily.get("sleepScores", {}).get("overall", {}).get("value"),
            hrv_nightly=raw.get("hrvSummary", {}).get("weeklyAvg"),
            raw_json=json.dumps(raw),
            synced_at=datetime.utcnow(),
        )

        if existing:
            for k, v in sleep_data.items():
                setattr(existing, k, v)
            updated += 1
        else:
            session.add(SleepRecord(**sleep_data))
            created += 1

    session.commit()
    return {"created": created, "updated": updated}


def get_activities(session: Session, days: int = 7) -> list[Activity]:
    cutoff = datetime.utcnow() - timedelta(days=days)
    return session.exec(
        select(Activity)
        .where(Activity.start_time >= cutoff)
        .order_by(Activity.start_time.desc())
    ).all()


def get_sleep_records(session: Session, days: int = 7) -> list[SleepRecord]:
    cutoff = (date.today() - timedelta(days=days)).isoformat()
    return session.exec(
        select(SleepRecord)
        .where(SleepRecord.date >= cutoff)
        .order_by(SleepRecord.date.desc())
    ).all()
