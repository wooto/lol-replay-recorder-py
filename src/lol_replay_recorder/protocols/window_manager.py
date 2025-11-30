"""
Protocol definitions for window management implementations.

This module provides protocol interfaces to standardize window and input
automation behavior across different platforms and libraries.
"""

from abc import ABC, abstractmethod
from enum import IntEnum
from typing import Optional, Tuple


class Key(IntEnum):
    """Enum representing keyboard keys mapped to integer values."""
    # Numbers row (0-9)
    KEY_0 = 0
    KEY_1 = 1
    KEY_2 = 2
    KEY_3 = 3
    KEY_4 = 4
    KEY_5 = 5
    KEY_6 = 6
    KEY_7 = 7
    KEY_8 = 8
    KEY_9 = 9

    # First row letters (Q-P)
    KEY_Q = 10
    KEY_W = 11
    KEY_E = 12
    KEY_R = 13
    KEY_T = 14
    KEY_Y = 15
    KEY_U = 16
    KEY_I = 17
    KEY_O = 18
    KEY_P = 19

    # Second row letters (A-L)
    KEY_A = 20
    KEY_S = 21
    KEY_D = 22
    KEY_F = 23
    KEY_G = 24
    KEY_H = 25
    KEY_J = 26
    KEY_K = 27
    KEY_L = 28

    # Third row letters (Z-M)
    KEY_Z = 29
    KEY_X = 30
    KEY_C = 31
    KEY_V = 32
    KEY_B = 33
    KEY_N = 34
    KEY_M = 35

    # Special keys
    KEY_SPACE = 36
    KEY_ENTER = 37
    KEY_ESCAPE = 38
    KEY_TAB = 39
    KEY_BACKSPACE = 40
    KEY_DELETE = 41

    # Arrow keys
    KEY_UP = 42
    KEY_DOWN = 43
    KEY_LEFT = 44
    KEY_RIGHT = 45

    # Function keys
    KEY_F1 = 46
    KEY_F2 = 47
    KEY_F3 = 48
    KEY_F4 = 49
    KEY_F5 = 50
    KEY_F6 = 51
    KEY_F7 = 52
    KEY_F8 = 53
    KEY_F9 = 54
    KEY_F10 = 55
    KEY_F11 = 56
    KEY_F12 = 57

    # Modifier keys
    KEY_SHIFT = 58
    KEY_CONTROL = 59
    KEY_ALT = 60
    KEY_COMMAND = 61  # Mac CMD key
    KEY_OPTION = 62   # Mac Option key

    # Additional keys for compatibility
    KEY_CAPS_LOCK = 63
    KEY_HOME = 64
    KEY_END = 65
    KEY_PAGE_UP = 66
    KEY_PAGE_DOWN = 67

    # Number pad
    KEY_NUMPAD_0 = 68
    KEY_NUMPAD_1 = 69
    KEY_NUMPAD_2 = 70
    KEY_NUMPAD_3 = 71
    KEY_NUMPAD_4 = 72
    KEY_NUMPAD_5 = 73
    KEY_NUMPAD_6 = 74
    KEY_NUMPAD_7 = 75
    KEY_NUMPAD_8 = 76
    KEY_NUMPAD_9 = 77

    # Punctuation and symbols
    KEY_MINUS = 78
    KEY_EQUALS = 79
    KEY_LEFT_BRACKET = 80
    KEY_RIGHT_BRACKET = 81
    KEY_BACKSLASH = 82
    KEY_SEMICOLON = 83
    KEY_APOSTROPHE = 84
    KEY_COMMA = 85
    KEY_PERIOD = 86
    KEY_SLASH = 87
    KEY_GRAVE = 88  # Backtick (`)


class WindowManager(ABC):
    """
    Protocol defining the interface for window management implementations.

    This protocol standardizes window automation operations including
    window focus, keyboard input, and mouse control across different platforms.
    """

    @abstractmethod
    def focus_window(self, title: str) -> bool:
        """
        Focus a window by title.

        Args:
            title: Window title to focus

        Returns:
            True if window was found and focused, False otherwise
        """
        pass

    @abstractmethod
    def get_window_bounds(self, title: str) -> Optional[Tuple[int, int, int, int]]:
        """
        Get window bounds (left, top, width, height).

        Args:
            title: Window title

        Returns:
            Tuple of (left, top, width, height) or None if window not found
        """
        pass

    @abstractmethod
    def press_key(self, key: Key) -> None:
        """
        Press and release a key.

        Args:
            key: Key to press
        """
        pass

    @abstractmethod
    def key_down(self, key: Key) -> None:
        """
        Press a key without releasing.

        Args:
            key: Key to press
        """
        pass

    @abstractmethod
    def key_up(self, key: Key) -> None:
        """
        Release a key.

        Args:
            key: Key to release
        """
        pass

    @abstractmethod
    def type_text(self, text: str) -> None:
        """
        Type text characters.

        Args:
            text: Text to type
        """
        pass

    @abstractmethod
    def mouse_click(self, x: int, y: int, button: str = "left") -> None:
        """
        Click mouse at coordinates.

        Args:
            x: X coordinate
            y: Y coordinate
            button: Mouse button ("left", "right", "middle")
        """
        pass

    @abstractmethod
    def mouse_move(self, x: int, y: int) -> None:
        """
        Move mouse to coordinates.

        Args:
            x: X coordinate
            y: Y coordinate
        """
        pass


class WindowManagerError(Exception):
    """Base exception for window manager errors."""
    pass