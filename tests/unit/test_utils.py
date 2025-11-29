import pytest
import time
from lol_replay_recorder.utils.utils import (
    convert_seconds_to_hms,
    format_date,
    convert_file_path,
    refine_region,
    millis_to_seconds,
    seconds_to_millis,
    sleep,
    sleep_in_seconds,
)
from datetime import datetime


@pytest.mark.asyncio
async def test_sleep_waits_correct_milliseconds():
    start = time.time()
    await sleep(100)  # 100ms
    elapsed = (time.time() - start) * 1000
    assert 95 <= elapsed <= 150  # Allow some tolerance


@pytest.mark.asyncio
async def test_sleep_in_seconds_waits_correct_seconds():
    start = time.time()
    await sleep_in_seconds(1)
    elapsed = time.time() - start
    assert 0.95 <= elapsed <= 1.1


@pytest.mark.asyncio
async def test_sleep_with_zero_returns_immediately():
    start = time.time()
    await sleep(0)
    elapsed = time.time() - start
    assert elapsed < 0.1


@pytest.mark.asyncio
async def test_sleep_with_negative_returns_immediately():
    start = time.time()
    await sleep(-5)
    elapsed = time.time() - start
    assert elapsed < 0.1


def test_convert_seconds_to_hms_with_hours():
    assert convert_seconds_to_hms(3661) == "1h 1m 1s"


def test_convert_seconds_to_hms_with_minutes_only():
    assert convert_seconds_to_hms(125) == "2m 5s"


def test_convert_seconds_to_hms_with_seconds_only():
    assert convert_seconds_to_hms(45) == "45s"


def test_convert_seconds_to_hms_with_zero():
    assert convert_seconds_to_hms(0) == "0s"


def test_format_date():
    date = datetime(2025, 11, 29, 15, 30)
    assert format_date(date) == "2025-11-29"


def test_convert_file_path():
    assert convert_file_path("C:/Riot Games/LoL") == "C:\\Riot Games\\LoL"


def test_refine_region():
    assert refine_region("na1") == "na"
    assert refine_region("euw1") == "euw"
    assert refine_region("kr") == "kr"


def test_millis_to_seconds():
    assert millis_to_seconds(1000) == 1.0
    assert millis_to_seconds(500) == 0.5


def test_seconds_to_millis():
    assert seconds_to_millis(1) == 1000
    assert seconds_to_millis(0.5) == 500