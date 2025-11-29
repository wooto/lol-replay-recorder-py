import pytest
import time
from lol_replay_recorder.utils.utils import sleep, sleep_in_seconds


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