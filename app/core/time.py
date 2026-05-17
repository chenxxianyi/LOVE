"""
Time and date utilities.
"""
from datetime import datetime, date, timedelta
from typing import Optional
import calendar


def now_str() -> str:
    """Get current datetime as ISO format string."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def now_date_str() -> str:
    """Get current date as string."""
    return date.today().strftime("%Y-%m-%d")


def parse_date(date_str: str) -> Optional[date]:
    """Parse a date string in YYYY-MM-DD format."""
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None


def parse_datetime(datetime_str: str) -> Optional[datetime]:
    """Parse a datetime string in various formats."""
    formats = ["%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d"]
    for fmt in formats:
        try:
            return datetime.strptime(datetime_str, fmt)
        except ValueError:
            continue
    return None


def format_date(dt: datetime | date, fmt: str = "%Y-%m-%d") -> str:
    """Format a date/datetime as string."""
    if isinstance(dt, datetime):
        return dt.strftime(fmt)
    return dt.strftime(fmt)


def days_between(start_date: date, end_date: date) -> int:
    """Calculate days between two dates."""
    return abs((end_date - start_date).days)


def days_until(target_date: date) -> int:
    """Calculate days until a target date from today."""
    return (target_date - date.today()).days


def get_next_anniversary_days(start_date: date) -> int:
    """
    Calculate days until the next anniversary.
    Handles edge cases like Feb 29.
    """
    today = date.today()
    start_month = start_date.month
    start_day = start_date.day

    def safe_anniversary(year: int) -> date:
        last_day = calendar.monthrange(year, start_month)[1]
        return date(year, start_month, min(start_day, last_day))

    anniversary_this_year = safe_anniversary(today.year)
    if today <= anniversary_this_year:
        next_anniversary = anniversary_this_year
    else:
        next_anniversary = safe_anniversary(today.year + 1)

    return (next_anniversary - today).days


def is_past_date(date_str: str) -> bool:
    """Check if a date string represents a past date."""
    parsed = parse_date(date_str)
    if parsed is None:
        return False
    return parsed < date.today()


def is_valid_date(date_str: str) -> bool:
    """Check if a date string is valid."""
    return parse_date(date_str) is not None