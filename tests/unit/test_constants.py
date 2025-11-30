"""Test that constants are properly defined and used."""

import pytest
from lol_replay_recorder.constants import (
    # Time constants
    DEFAULT_TIMEOUT,
    LOCKFILE_WAIT_TIMEOUT,
    REPLAY_ASSETS_WAIT_TIMEOUT,
    REPLAY_READY_TIMEOUT,

    # Retry constants
    DEFAULT_RETRY_COUNT,
    HTTP_RETRY_COUNT,
    REPLAY_READY_RETRY_COUNT,

    # Network constants
    RIOT_REPLAY_API_HOST,
    RIOT_REPLAY_API_PORT,
    RIOT_REPLAY_BASE_URL,

    # Platform constants
    PLATFORM_WINDOWS,
    PLATFORM_DARWIN,
    PLATFORM_LINUX,

    # Process names
    LEAGUE_CLIENT_PROCESS,
    LEAGUE_OF_LEGENDS_PROCESS,

    # File names
    LOCKFILE_NAME,
    INPUT_INI_NAME,
    GAME_CFG_NAME,
)


class TestConstants:
    """Test constant definitions and values."""

    def test_time_constants_are_positive(self):
        """Test that time-related constants are positive numbers."""
        assert DEFAULT_TIMEOUT > 0
        assert LOCKFILE_WAIT_TIMEOUT > 0
        assert REPLAY_ASSETS_WAIT_TIMEOUT > 0
        assert REPLAY_READY_TIMEOUT > 0

    def test_retry_counts_are_positive_integers(self):
        """Test that retry count constants are positive integers."""
        assert isinstance(DEFAULT_RETRY_COUNT, int)
        assert DEFAULT_RETRY_COUNT > 0
        assert isinstance(HTTP_RETRY_COUNT, int)
        assert HTTP_RETRY_COUNT > 0
        assert isinstance(REPLAY_READY_RETRY_COUNT, int)
        assert REPLAY_READY_RETRY_COUNT > 0

    def test_network_constants(self):
        """Test network-related constants."""
        assert RIOT_REPLAY_API_HOST == "127.0.0.1"
        assert RIOT_REPLAY_API_PORT == 2999
        assert RIOT_REPLAY_BASE_URL == f"https://{RIOT_REPLAY_API_HOST}:{RIOT_REPLAY_API_PORT}"

    def test_platform_constants(self):
        """Test platform name constants."""
        assert PLATFORM_WINDOWS == "Windows"
        assert PLATFORM_DARWIN == "Darwin"
        assert PLATFORM_LINUX == "Linux"

    def test_process_names_end_with_exe(self):
        """Test that Windows process names end with .exe."""
        assert LEAGUE_CLIENT_PROCESS.endswith(".exe")
        assert LEAGUE_OF_LEGENDS_PROCESS.endswith(".exe")

    def test_file_names(self):
        """Test file name constants."""
        assert LOCKFILE_NAME == "lockfile"
        assert INPUT_INI_NAME == "input.ini"
        assert GAME_CFG_NAME == "game.cfg"


class TestHTTPClientConstants:
    """Test HTTP client specific constants."""

    def test_http_constants_import(self):
        """Test that HTTP client constants can be imported."""
        from lol_replay_recorder.clients.http.constants import (
            VERIFY_SSL_DEFAULT,
            HTTP_NOT_FOUND,
            RIOT_AUTH_USERNAME,
            LOCKFILE_PARTS_COUNT,
        )

        # Test values
        assert VERIFY_SSL_DEFAULT is False
        assert HTTP_NOT_FOUND == 404
        assert RIOT_AUTH_USERNAME == "riot"
        assert LOCKFILE_PARTS_COUNT == 5


class TestControllerConstants:
    """Test controller specific constants."""

    def test_controller_constants_import(self):
        """Test that controller constants can be imported."""
        from lol_replay_recorder.controllers.constants import (
            LEAGUE_CLIENT_WINDOW_TITLE,
            CAMERA_FOCUS_RETRY_COUNT,
            PLAYER_SELECTION_KEYS_ORDER,
            PLAYER_SELECTION_KEYS_CHAOS,
        )

        # Test values
        assert LEAGUE_CLIENT_WINDOW_TITLE == "League Client"
        assert isinstance(CAMERA_FOCUS_RETRY_COUNT, int)
        assert CAMERA_FOCUS_RETRY_COUNT > 0

        # Test key bindings
        assert len(PLAYER_SELECTION_KEYS_ORDER) == 5
        assert len(PLAYER_SELECTION_KEYS_CHAOS) == 5
        assert PLAYER_SELECTION_KEYS_ORDER == ["1", "2", "3", "4", "5"]
        assert PLAYER_SELECTION_KEYS_CHAOS == ["Q", "W", "E", "R", "T"]