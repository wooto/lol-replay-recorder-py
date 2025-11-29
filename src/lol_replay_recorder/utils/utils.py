import asyncio
import re
from datetime import datetime
from typing import Any


async def sleep(ms: int | float) -> None:
    """Sleep for specified milliseconds."""
    if ms <= 0:
        return
    await asyncio.sleep(ms / 1000)


async def sleep_in_seconds(s: int | float) -> None:
    """Sleep for specified seconds."""
    if s <= 0:
        return
    await asyncio.sleep(s)


def millis_to_seconds(ms: int | float) -> float:
    """Convert milliseconds to seconds."""
    return ms * 0.001


def seconds_to_millis(s: int | float) -> float:
    """Convert seconds to milliseconds."""
    return s * 1000


def convert_seconds_to_hms(s: float) -> str:
    """Format seconds in a nicely formatted string (e.g., '1h 23m 45s')."""
    seconds = round(s)
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    remaining_seconds = seconds % 60

    parts = []
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")
    if remaining_seconds > 0 or len(parts) == 0:
        parts.append(f"{remaining_seconds}s")

    return " ".join(parts)


def format_date(raw_date: Any) -> str:
    """Returns a new datetime in YYYY-MM-DD format."""
    if isinstance(raw_date, datetime):
        return raw_date.date().isoformat()
    return datetime.fromisoformat(str(raw_date)).date().isoformat()


def convert_file_path(path: str) -> str:
    """Replace forward slashes in file path with back slashes (Windows)."""
    return path.replace("/", "\\")


def refine_region(region: str) -> str:
    """Remove digits from region string."""
    return re.sub(r"\d", "", region)