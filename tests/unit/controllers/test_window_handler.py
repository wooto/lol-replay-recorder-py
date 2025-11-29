import pytest
from unittest.mock import AsyncMock, patch
from lol_replay_recorder.controllers.window_handler import (
    Key,
    Region,
    WindowHandler,
)


def test_key_enum_has_expected_values():
    assert Key.Escape == 0
    assert Key.Num1 == 29
    assert Key.Q == 50
    assert Key.Enter == 102


def test_region_initialization():
    region = Region(10, 20, 800, 600)
    assert region.left == 10
    assert region.top == 20
    assert region.width == 800
    assert region.height == 600


def test_region_area():
    region = Region(0, 0, 100, 50)
    assert region.area() == 5000


@pytest.mark.asyncio
async def test_window_handler_keyboard_type():
    handler = WindowHandler()

    with patch("pyautogui.press") as mock_press:
        await handler.keyboard_type(Key.Enter)
        mock_press.assert_called_once()


@pytest.mark.asyncio
async def test_window_handler_focus_window():
    handler = WindowHandler()

    mock_window = AsyncMock()
    mock_window.title = "Test Window"
    mock_window.left = 100
    mock_window.top = 100
    mock_window.width = 800
    mock_window.height = 600

    with patch("pygetwindow.getWindowsWithTitle", return_value=[mock_window]):
        with patch("pyautogui.click"):
            await handler.focus_client_window("Test Window")