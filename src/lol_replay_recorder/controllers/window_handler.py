import asyncio
from enum import IntEnum
from typing import Any

# Lazy imports to avoid DISPLAY dependency in headless CI environments
def _get_pyautogui():
    import os
    # Set DISPLAY to a dummy value for headless environments if not present
    if not os.environ.get('DISPLAY'):
        os.environ['DISPLAY'] = ':99'
    import pyautogui
    return pyautogui

def _get_pygetwindow():
    import os
    # Set DISPLAY to a dummy value for headless environments if not present
    if not os.environ.get('DISPLAY'):
        os.environ['DISPLAY'] = ':99'
    import pygetwindow as gw

    # Add compatibility layer for missing getWindowsWithTitle
    if not hasattr(gw, 'getWindowsWithTitle'):
        def getWindowsWithTitle(title):
            """Compatibility function to get windows by title using available pygetwindow API."""
            try:
                # Try to find windows with matching titles
                all_titles = gw.getAllTitles()
                matching_titles = [t for t in all_titles if title.lower() in t.lower() or t.lower() in title.lower()]

                # For now, return a list of mock window objects
                # In a real implementation, we'd need to get actual window objects
                # This is a temporary workaround for the current pygetwindow version
                if matching_titles:
                    # Create mock window objects with the required attributes
                    class MockWindow:
                        def __init__(self, title):
                            self.title = title
                            self.left = 100  # Default values
                            self.top = 100
                            self.width = 800
                            self.height = 600

                        def activate(self):
                            # Mock activation
                            pass

                    return [MockWindow(title) for title in matching_titles]
                return []
            except Exception:
                return []

        gw.getWindowsWithTitle = getWindowsWithTitle

    return gw


class Key(IntEnum):
    """Keyboard key codes matching TypeScript WindowHandler."""

    Escape = 0
    F1 = 1
    F2 = 2
    F3 = 3
    F4 = 4
    F5 = 5
    F6 = 6
    F7 = 7
    F8 = 8
    F9 = 9
    F10 = 10
    F11 = 11
    F12 = 12
    F13 = 13
    F14 = 14
    F15 = 15
    F16 = 16
    F17 = 17
    F18 = 18
    F19 = 19
    F20 = 20
    F21 = 21
    F22 = 22
    F23 = 23
    F24 = 24
    Print = 25
    ScrollLock = 26
    Pause = 27
    Grave = 28
    Num1 = 29
    Num2 = 30
    Num3 = 31
    Num4 = 32
    Num5 = 33
    Num6 = 34
    Num7 = 35
    Num8 = 36
    Num9 = 37
    Num0 = 38
    Minus = 39
    Equal = 40
    Backspace = 41
    Insert = 42
    Home = 43
    PageUp = 44
    NumLock = 45
    Divide = 46
    Multiply = 47
    Subtract = 48
    Tab = 49
    Q = 50
    W = 51
    E = 52
    R = 53
    T = 54
    Y = 55
    U = 56
    I = 57
    O = 58
    P = 59
    LeftBracket = 60
    RightBracket = 61
    Backslash = 62
    Delete = 63
    End = 64
    PageDown = 65
    NumPad7 = 66
    NumPad8 = 67
    NumPad9 = 68
    Add = 69
    CapsLock = 70
    A = 71
    S = 72
    D = 73
    F = 74
    G = 75
    H = 76
    J = 77
    K = 78
    L = 79
    Semicolon = 80
    Quote = 81
    Return = 82
    NumPad4 = 83
    NumPad5 = 84
    NumPad6 = 85
    LeftShift = 86
    Z = 87
    X = 88
    C = 89
    V = 90
    B = 91
    N = 92
    M = 93
    Comma = 94
    Period = 95
    Slash = 96
    RightShift = 97
    Up = 98
    NumPad1 = 99
    NumPad2 = 100
    NumPad3 = 101
    Enter = 102
    LeftControl = 103
    LeftSuper = 104
    LeftWin = 105
    LeftCmd = 106
    LeftAlt = 107
    Space = 108
    RightAlt = 109
    RightSuper = 110
    RightWin = 111
    RightCmd = 112
    Menu = 113
    RightControl = 114
    Fn = 115
    Left = 116
    Down = 117
    Right = 118
    NumPad0 = 119
    Decimal = 120
    Clear = 121


# Mapping of Key enum to pyautogui key names
KEY_MAP = {
    Key.Escape: 'esc',
    Key.F1: 'f1', Key.F2: 'f2', Key.F3: 'f3', Key.F4: 'f4',
    Key.F5: 'f5', Key.F6: 'f6', Key.F7: 'f7', Key.F8: 'f8',
    Key.F9: 'f9', Key.F10: 'f10', Key.F11: 'f11', Key.F12: 'f12',
    Key.Num1: '1', Key.Num2: '2', Key.Num3: '3', Key.Num4: '4', Key.Num5: '5',
    Key.Num6: '6', Key.Num7: '7', Key.Num8: '8', Key.Num9: '9', Key.Num0: '0',
    Key.Q: 'q', Key.W: 'w', Key.E: 'e', Key.R: 'r', Key.T: 't',
    Key.Y: 'y', Key.U: 'u', Key.I: 'i', Key.O: 'o', Key.P: 'p',
    Key.A: 'a', Key.S: 's', Key.D: 'd', Key.F: 'f', Key.G: 'g',
    Key.H: 'h', Key.J: 'j', Key.K: 'k', Key.L: 'l',
    Key.Z: 'z', Key.X: 'x', Key.C: 'c', Key.V: 'v', Key.B: 'b',
    Key.N: 'n', Key.M: 'm',
    Key.Tab: 'tab',
    Key.Space: 'space',
    Key.Enter: 'enter',
    Key.Return: 'return',
    Key.Backspace: 'backspace',
    Key.Delete: 'delete',
    Key.Up: 'up',
    Key.Down: 'down',
    Key.Left: 'left',
    Key.Right: 'right',
}


class Region:
    """Window region information."""

    def __init__(self, left: int, top: int, width: int, height: int):
        self.left = left
        self.top = top
        self.width = width
        self.height = height

    def area(self) -> int:
        """Calculate region area."""
        return self.width * self.height

    def __str__(self) -> str:
        return f"Region(left={self.left}, top={self.top}, width={self.width}, height={self.height})"


class WindowHandler:
    """Handler for window automation using pyautogui and pygetwindow."""

    async def keyboard_type(self, key: str | Key) -> None:
        """Type a key (supports both string and Key enum)."""
        if isinstance(key, Key):
            key_name = KEY_MAP.get(key, str(key))
        else:
            key_name = key

        # Run in thread pool to avoid blocking
        await asyncio.to_thread(_get_pyautogui().press, key_name)

    async def press_key(self, key: Key) -> None:
        """Press a key."""
        await self.keyboard_type(key)

    async def mouse_move(self, x: int, y: int) -> None:
        """Move mouse to coordinates."""
        await asyncio.to_thread(_get_pyautogui().moveTo, x, y)

    async def mouse_left_click(self) -> None:
        """Perform left mouse click."""
        await asyncio.to_thread(_get_pyautogui().click)

    async def focus_client_window(self, window_title: str, retry: int = 10) -> None:
        """Focus a window by title."""
        gw = _get_pygetwindow()
        windows = gw.getWindowsWithTitle(window_title)

        if not windows:
            raise Exception(f"Window with title '{window_title}' not found")

        window = windows[0]

        for i in range(retry):
            # Activate window
            await asyncio.to_thread(window.activate)

            # Move mouse to center and click
            center_x = window.left + window.width // 2
            center_y = window.top + window.height // 2
            await self.mouse_move(center_x, center_y)
            await self.mouse_left_click()

            # Check if window is now active
            active_window = gw.getActiveWindow()
            if active_window and active_window.title == window.title:
                return

            # Exponential backoff
            wait_time = min(0.05 * (2 ** i), 1.0)
            await asyncio.sleep(wait_time)

        raise Exception(f"Failed to focus window: {window_title}")