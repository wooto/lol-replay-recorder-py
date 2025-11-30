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
    get_riot_id,
    truncate_patch_version,
    is_match_on_current_patch,
    seconds_to_minutes_formatted,
    is_empty,
    splice_string,
)
from datetime import datetime


@pytest.mark.asyncio
@pytest.mark.unit
async def test_sleep_waits_correct_milliseconds():
    start = time.time()
    await sleep(100)  # 100ms
    elapsed = (time.time() - start) * 1000
    assert 95 <= elapsed <= 150  # Allow some tolerance


@pytest.mark.asyncio
@pytest.mark.unit
async def test_sleep_in_seconds_waits_correct_seconds():
    start = time.time()
    await sleep_in_seconds(1)
    elapsed = time.time() - start
    assert 0.95 <= elapsed <= 1.1


@pytest.mark.asyncio
@pytest.mark.unit
async def test_sleep_with_zero_returns_immediately():
    start = time.time()
    await sleep(0)
    elapsed = time.time() - start
    assert elapsed < 0.1


@pytest.mark.asyncio
@pytest.mark.unit
async def test_sleep_with_negative_returns_immediately():
    start = time.time()
    await sleep(-5)
    elapsed = time.time() - start
    assert elapsed < 0.1


@pytest.mark.unit
def test_convert_seconds_to_hms_with_hours():
    assert convert_seconds_to_hms(3661) == "1h 1m 1s"


@pytest.mark.unit
def test_convert_seconds_to_hms_with_minutes_only():
    assert convert_seconds_to_hms(125) == "2m 5s"


@pytest.mark.unit
def test_convert_seconds_to_hms_with_seconds_only():
    assert convert_seconds_to_hms(45) == "45s"


@pytest.mark.unit
def test_convert_seconds_to_hms_with_zero():
    assert convert_seconds_to_hms(0) == "0s"


@pytest.mark.unit
def test_format_date():
    date = datetime(2025, 11, 29, 15, 30)
    assert format_date(date) == "2025-11-29"


@pytest.mark.unit
def test_convert_file_path():
    assert convert_file_path("C:/Riot Games/LoL") == "C:\\Riot Games\\LoL"


@pytest.mark.unit
def test_refine_region():
    assert refine_region("na1") == "na"
    assert refine_region("euw1") == "euw"
    assert refine_region("kr") == "kr"


@pytest.mark.unit
def test_millis_to_seconds():
    assert millis_to_seconds(1000) == 1.0
    assert millis_to_seconds(500) == 0.5


@pytest.mark.unit
def test_seconds_to_millis():
    assert seconds_to_millis(1) == 1000
    assert seconds_to_millis(0.5) == 500


@pytest.mark.unit
def test_get_riot_id():
    assert get_riot_id("PlayerName", "1234") == "PlayerName1234"
    assert get_riot_id("Test", "na1") == "Testna1"
    assert get_riot_id("", "TAG") == "TAG"
    assert get_riot_id("User", "") == "User"


@pytest.mark.unit
def test_truncate_patch_version():
    assert truncate_patch_version("13.1.123.456") == "13.1"
    assert truncate_patch_version("12.5.321") == "12.5"
    assert truncate_patch_version("11.23") == "11.23"
    assert truncate_patch_version("10.7.1") == "10.7"


@pytest.mark.unit
def test_is_match_on_current_patch():
    match = {"gameVersion": "13.1.123.456"}
    current_patch = "13.1.321.789"
    assert is_match_on_current_patch(match, current_patch) == True

    match_diff = {"gameVersion": "12.5.123.456"}
    assert is_match_on_current_patch(match_diff, current_patch) == False

    match_exact = {"gameVersion": "13.1"}
    assert is_match_on_current_patch(match_exact, current_patch) == True


@pytest.mark.unit
def test_seconds_to_minutes_formatted():
    assert seconds_to_minutes_formatted(120) == "2m : 0s"
    assert seconds_to_minutes_formatted(90) == "1m : 30s"
    assert seconds_to_minutes_formatted(30) == "0m : 30s"
    assert seconds_to_minutes_formatted(3630) == "60m : 30s"
    assert seconds_to_minutes_formatted(0) == "0m : 0s"


@pytest.mark.unit
def test_is_empty():
    assert is_empty({}) == True
    assert is_empty({"key": "value"}) == False
    assert is_empty({"nested": {}}) == False


@pytest.mark.unit
def test_splice_string():
    assert splice_string("hello world", 6, " ") == "world"
    assert splice_string("test-string", 5, "-") == "string"
    assert splice_string("filename.txt", 0, ".") == "filename"
    assert splice_string("path/to/file", 5, "/") == "to"