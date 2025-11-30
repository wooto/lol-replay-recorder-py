"""
Common constants used throughout the application.

This module contains magic numbers, hardcoded strings, and other constants
that are used across multiple components of the application.
"""

# Time and timeout constants (in seconds unless specified)
DEFAULT_TIMEOUT = 30.0
LOCKFILE_WAIT_TIMEOUT = 60.0
REPLAY_ASSETS_WAIT_TIMEOUT = 15.0
REPLAY_READY_TIMEOUT = 60.0
REPLAY_READY_CHECK_INTERVAL = 1.0
REPLAY_RENDER_ASSETS_TIMEOUT = 10.0
LOCKFILE_EXIST_TIMEOUT_MS = 60000  # milliseconds
SHORT_WAIT = 5.0
MINUTE_IN_SECONDS = 60
HOUR_IN_SECONDS = 3600

# Retry count constants
DEFAULT_RETRY_COUNT = 3
HTTP_RETRY_COUNT = 5
RIOT_API_RETRY_COUNT = 5
REPLAY_READY_RETRY_COUNT = 10
PROCESS_WAIT_RETRY_COUNT = 10
LOCKFILE_WAIT_RETRY_COUNT = 30
GAME_LAUNCH_RETRY_COUNT = 30
PROCESS_LAUNCH_RETRY_COUNT = 10
PROCESS_CLEANUP_RETRY_COUNT = 30
WINDOW_FOCUS_RETRY_COUNT = 10

# Network constants
RIOT_REPLAY_API_HOST = "127.0.0.1"
RIOT_REPLAY_API_PORT = 2999
RIOT_REPLAY_BASE_URL = f"https://{RIOT_REPLAY_API_HOST}:{RIOT_REPLAY_API_PORT}"
LOCALHOST = "localhost"

# Platform names
PLATFORM_WINDOWS = "Windows"
PLATFORM_DARWIN = "Darwin"  # macOS
PLATFORM_LINUX = "Linux"

# Process names (Windows)
RIOT_CLIENT_UX_PROCESS = "RiotClientUx.exe"
RIOT_CLIENT_SERVICES_PROCESS = "RiotClientServices.exe"
RIOT_CLIENT_PROCESS = "RiotClient.exe"
RIOT_CLIENT_LEGACY_PROCESS = "Riot Client.exe"
LEAGUE_CLIENT_PROCESS = "LeagueClient.exe"
LEAGUE_OF_LEGENDS_PROCESS = "League of Legends.exe"
LEAGUE_CLIENT_UX_RENDER_PROCESS = "LeagueClientUxRender.exe"

# File extensions
EXECUTABLE_EXTENSION = ".exe"
MAC_APP_EXTENSION = ".app"
CONFIG_EXTENSION_INI = ".ini"
CONFIG_EXTENSION_YAML = ".yaml"

# File names
LOCKFILE_NAME = "lockfile"
INPUT_INI_NAME = "input.ini"
GAME_CFG_NAME = "game.cfg"
PRODUCT_SETTINGS_YAML_NAME = "product_settings.yaml"

# Directory names
CONFIG_DIR = "Config"
GAME_DIR = "Game"
MACOS_DIR = "MacOS"
CONTENTS_DIR = "Contents"
LOL_DIR = "LoL"

# Riot Games directory structure
RIOT_GAMES = "Riot Games"
LEAGUE_OF_LEGENDS = "League of Legends"
RIOT_CLIENT_DIR = "Riot Client"
METADATA_DIR = "Metadata"

# HTTP and API constants
HTTP_GET = "GET"
HTTP_POST = "POST"
HTTP_PUT = "PUT"
HTTP_DELETE = "DELETE"
AUTHORIZATION_HEADER = "Authorization"
BASIC_AUTH_PREFIX = "Basic"

# League Client API endpoints
LCU_HIGHLIGHTS_FOLDER_PATH_ENDPOINT = "/lol-highlights/v1/highlights-folder-path"

# Game constants
MIN_PLAYERS_PER_TEAM = 1
MAX_PLAYERS_PER_TEAM = 5
ORDER_TEAM_PLAYERS_START = 1
CHAOS_TEAM_PLAYERS_START = 5
CAMERA_FOCUS_DELAY_TIME = 0.5

# Configuration sections and keys
GENERAL_SECTION = "General"
LOL_HIGH_FOLDER_SECTION = "LoLHighFolder"
ENABLE_REPLAY_API_KEY = "EnableReplayApi"
KEYbinds_SECTION = "Keybinds"
GAME_EVENTS_SECTION = "GameEvents"

# Event names
EVT_SELECT_ORDER_PLAYER_PREFIX = "evtSelectOrderPlayer"
EVT_SELECT_CHAOS_PLAYER_PREFIX = "evtSelectChaosPlayer"

# Time formatting
TIME_FORMAT_HOURS = "h"
TIME_FORMAT_MINUTES = "m"
TIME_FORMAT_SECONDS = "s"

# Patch version formatting (one decimal place)
PATCH_VERSION_DECIMAL_PLACES = 1

# Rounding constants for time conversion
SECONDS_PER_MINUTE = 60
SECONDS_PER_HOUR = 3600
ROUND_SECONDS_TO_INT = 0