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


def get_riot_id(summoner_name: str, tagline: str) -> str:
    """Combine summoner name and tagline to create Riot ID."""
    return f"{summoner_name}{tagline}"


def truncate_patch_version(raw_patch_data: str) -> str:
    """Shortens raw patch string to one decimal place (e.g. 11.7, 12.13, 10.9)."""
    tokens = raw_patch_data.split('.')
    if len(tokens) < 2:
        return raw_patch_data
    return f"{tokens[0]}.{tokens[1]}"


def is_match_on_current_patch(match: dict, raw_current_patch_data: str) -> bool:
    """Check if match is on current patch by comparing truncated version strings."""
    raw_match_patch_data = match.get('gameVersion', '')
    match_patch = truncate_patch_version(raw_match_patch_data)
    current_patch = truncate_patch_version(raw_current_patch_data)
    return match_patch == current_patch


def seconds_to_minutes_formatted(s: float) -> str:
    """Format seconds as minutes and seconds (e.g., '2m : 30s')."""
    minutes = s / 60
    seconds_float = minutes - int(minutes)
    minutes = int(minutes)
    seconds_int = int(round(seconds_float * 60))

    # Handle case where rounding pushes seconds to 60
    if seconds_int == 60:
        minutes += 1
        seconds_int = 0

    seconds_string = f"{seconds_int}"
    return f"{minutes}m : {seconds_string}s"


def is_empty(obj: dict) -> bool:
    """Check if dictionary is empty."""
    return len(obj.keys()) == 0


def splice_string(text: str, start_index: int, end_char: str) -> str:
    """Extract substring from start_index until end_char is found (exclusive)."""
    spliced_string = ""
    for i in range(start_index, len(text)):
        if text[i] == end_char:
            break
        spliced_string += text[i]
    return spliced_string