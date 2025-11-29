# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A Python library for recording League of Legends replays. The library provides APIs to interact with:
- League Client Update (LCU) API - for client state and authentication
- Riot Replay API - for controlling replay playback and recording
- Window automation - for camera control and UI interaction during replay

## Development Commands

```bash
# Install dependencies
poetry install

# Run all tests
poetry run pytest

# Run only unit tests
poetry run pytest -m unit

# Run only e2e tests (requires League client)
poetry run pytest -m e2e

# Run a single test file
poetry run pytest tests/unit/test_utils.py

# Run a specific test
poetry run pytest tests/unit/test_utils.py::test_sleep_waits_correct_milliseconds

# Type checking
poetry run mypy src/

# Linting
poetry run ruff check src/
```

## Architecture

### Core Components

**Controllers** (`src/lol_replay_recorder/controllers/`)
- `LeagueReplayClient` - Primary interface for replay control via Riot's Replay API (port 2999)
  - Manages replay playback, recording, and rendering properties
  - Handles camera focusing on specific summoners
  - Provides async methods for all replay operations
- `WindowHandler` - Low-level keyboard/mouse automation using pyautogui and pygetwindow
  - Maps custom Key enum to pyautogui key names
  - Focuses windows, sends keyboard input, and controls mouse

**API Clients** (`src/lol_replay_recorder/models/`)
- `lcu_request.py` - Authenticates with League Client via lockfile, makes LCU API requests
  - Waits for lockfile existence (up to 60s timeout)
  - Extracts port and password for basic auth
- `riot_request.py` - Makes HTTP requests to Riot Replay API with retry logic
  - Disables SSL verification (self-signed certs)
  - Returns CustomError on 404, retries on other failures

**Configuration Editors** (`src/lol_replay_recorder/apis/`)
- `IniEditor` - Loads/saves INI files, preserves key case
- `YamlEditor` - Loads/saves YAML files with dot-notation updates

**Models** (`src/lol_replay_recorder/models/`)
- Type definitions for API responses (RecordingProperties, RenderProperties, GameData)
- Custom error types
- Enums for locales and replay types

### Key Patterns

**Authentication Flow**
1. Read lockfile from League Client installation directory
2. Parse format: `LeagueClient:PID:PORT:PASSWORD:PROTOCOL`
3. Create basic auth header: `Basic base64(riot:PASSWORD)`
4. Make requests to `https://127.0.0.1:PORT/endpoint`

**Replay Control Flow**
1. Initialize `LeagueReplayClient` and call `init()` to get process ID
2. Call `load(timeout, retries)` which waits for replay API availability
3. Waits for assets (time >= 15s or paused)
4. Use playback/recording/render property methods to control replay
5. Call `exit()` to kill replay process when done

**Window Automation**
- Uses custom Key enum (IntEnum 0-121) matching TypeScript implementation
- Maps to pyautogui key strings via KEY_MAP dictionary
- All async operations use `asyncio.to_thread()` to avoid blocking

### Testing Structure

- `tests/unit/` - Unit tests using pytest, pytest-mock
- `tests/e2e/` - End-to-end tests requiring League client (marked with `@pytest.mark.e2e`)
- Tests use `@pytest.mark.asyncio` for async functions
- Async mode is set to "auto" in pyproject.toml

## Important Notes

- All HTTP clients disable SSL verification due to Riot's self-signed certificates
- The replay API runs on localhost:2999 when a replay is active
- LCU API port is dynamic, read from lockfile each time
- Window automation requires the League client window to be focused and visible
- Player positions map to keyboard keys: 1-5 for ORDER team, Q-T for CHAOS team (indices 0-9)
