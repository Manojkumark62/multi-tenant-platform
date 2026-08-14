from datetime import datetime, timedelta, timezone

def utc_now() -> datetime:
    return datetime.now(timezone.utc)

def utc_now_naive() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)

def add_minutes(minutes: int) -> datetime:
    return utc_now_naive() + timedelta(minutes=minutes)

def add_hours(hours: int) -> datetime:
    return utc_now_naive() + timedelta(hours=hours)

def add_days(days: int) -> datetime:
    return utc_now_naive() + timedelta(days=days)

def is_expired(expires_at: datetime) -> bool:
    current_time = utc_now_naive()
    if expires_at.tzinfo is not None:
        expires_at = expires_at.astimezone(timezone.utc).replace(tzinfo=None)
    return current_time >= expires_at