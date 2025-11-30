import pytest
from unittest.mock import AsyncMock, MagicMock, patch
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

    with patch("lol_replay_recorder.controllers.window_handler._get_pyautogui") as mock_get_pyautogui:
        mock_pyautogui = MagicMock()
        mock_get_pyautogui.return_value = mock_pyautogui

        await handler.keyboard_type(Key.Enter)
        mock_pyautogui.press.assert_called_once()


@pytest.mark.asyncio
async def test_window_handler_focus_window():
    handler = WindowHandler()

    mock_window = MagicMock()
    mock_window.title = "Test Window"
    mock_window.left = 100
    mock_window.top = 100
    mock_window.width = 800
    mock_window.height = 600

    with patch("lol_replay_recorder.controllers.window_handler._get_pygetwindow") as mock_get_gw:
        # Mock the pygetwindow module with the current API
        mock_gw = MagicMock()
        mock_gw.getAllTitles.return_value = ["Test Window", "Other Window"]
        mock_gw.getActiveWindow.return_value = mock_window
        mock_gw.getWindowsWithTitle.return_value = [mock_window]
        mock_get_gw.return_value = mock_gw

        with patch("lol_replay_recorder.controllers.window_handler._get_pyautogui"):
            await handler.focus_client_window("Test Window")

            # Verify that getWindowsWithTitle was called with the correct title
            mock_gw.getWindowsWithTitle.assert_called_once_with("Test Window")