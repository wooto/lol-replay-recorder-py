"""
Constants for process management services.

This module contains constants used by process management, platform detection,
and game client interaction services.
"""

import os

from ...constants import (
    PLATFORM_WINDOWS,
    PLATFORM_DARWIN,
    PLATFORM_LINUX,
    RIOT_CLIENT_UX_PROCESS,
    RIOT_CLIENT_SERVICES_PROCESS,
    RIOT_CLIENT_PROCESS,
    RIOT_CLIENT_LEGACY_PROCESS,
    LEAGUE_CLIENT_PROCESS,
    LEAGUE_OF_LEGENDS_PROCESS,
    LEAGUE_CLIENT_UX_RENDER_PROCESS,
    LOCKFILE_EXIST_TIMEOUT_MS,
    SHORT_WAIT,
    GAME_LAUNCH_RETRY_COUNT,
    PROCESS_LAUNCH_RETRY_COUNT,
    PROCESS_CLEANUP_RETRY_COUNT,
    LOCKFILE_WAIT_RETRY_COUNT,
)

# Windows installation paths
DEFAULT_WINDOWS_INSTALL_PATH = "C:\\Riot Games\\League of Legends"
DEFAULT_WINDOWS_RIOT_CLIENT_PATH = "C:\\Riot Games\\Riot Client\\RiotClientServices.exe"

# macOS installation paths
MAC_APPLICATIONS_PATH = "/Applications"
MAC_USER_APPLICATIONS_PATH = os.path.expanduser("~/Applications")
MAC_LOL_APP_PATH = "/Applications/League of Legends.app/Contents/LoL"
MAC_USER_LOL_APP_PATH = os.path.expanduser("~/Applications/League of Legends.app/Contents/LoL")
MAC_LEAGUE_CLIENT_PATH = "/Applications/League of Legends.app/Contents/MacOS/LeagueClient"
MAC_USER_LEAGUE_CLIENT_PATH = os.path.expanduser("~/Applications/League of Legends.app/Contents/MacOS/LeagueClient")

# Linux installation paths
LINUX_CONFIG_PATH = os.path.expanduser("~/.config/Riot Games/League of Legends")

# Platform-specific directory names
PROGRAM_DATA = "ProgramData"
LOCAL_APP_DATA = "LOCALAPPDATA"
PROGRAM_FILES = "ProgramFiles"
APPLICATION_SUPPORT = "Application Support"
LIBRARY = "Library"
CONFIG = "Config"

# Riot Games directory structure constants
RIOT_GAMES_METADATA_PATH = "Metadata/league_of_legends.live"
LEAGUE_LIVE_SETTINGS_FILE = "league_of_legends.live.product_settings.yaml"

# Process states and actions
PROCESS_STATE_IDLE = "Idle"
PROCESS_STATE_RUNNING = "Running"
PROCESS_STATE_STOPPED = "Stopped"

# File paths and patterns
WILDCARD_ANY = "*"
PATH_SEPARATOR = "\\"
UNIX_PATH_SEPARATOR = "/"

# Timeout values (in milliseconds where specified)
PROCESS_LAUNCH_WAIT_MS = 1000
PROCESS_CHECK_INTERVAL_MS = 500
PROCESS_TERMINATION_WAIT_MS = 5000

# Process management constants
MAX_PROCESS_TERMINATION_ATTEMPTS = 3
PROCESS_CLEANUP_DELAY_SECONDS = 2

# Game client states
CLIENT_STATE_IDLE = "Idle"
CLIENT_STATE_LAUNCHING = "Launching"
CLIENT_STATE_RUNNING = "Running"
CLIENT_STATE_CONNECTED = "Connected"
CLIENT_STATE_DISCONNECTED = "Disconnected"

# Login parameters
LOGIN_PARAM_USERNAME = "username"
LOGIN_PARAM_PASSWORD = "password"
LOGIN_PARAM_REGION = "region"

# Riot process termination priority (order of termination)
RIOT_PROCESSES_TERMINATION_ORDER = [
    LEAGUE_CLIENT_UX_RENDER_PROCESS,
    LEAGUE_OF_LEGENDS_PROCESS,
    LEAGUE_CLIENT_PROCESS,
    RIOT_CLIENT_LEGACY_PROCESS,
    RIOT_CLIENT_PROCESS,
    RIOT_CLIENT_UX_PROCESS,
    RIOT_CLIENT_SERVICES_PROCESS,
]