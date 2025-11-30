# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A Python library for recording League of Legends replays. The library provides APIs to interact with:
- League Client Update (LCU) API - for client state and authentication
- Riot Replay API - for controlling replay playback and recording
- Window automation - for camera control and UI interaction during replay

## Development Commands

```bash
# Install dependencies (creates .venv automatically)
uv sync

# Run all tests
uv run pytest

# Run only unit tests
uv run pytest -m unit

# Run only e2e tests (requires League client)
uv run pytest -m e2e

# Run a single test file
uv run pytest tests/unit/test_utils.py

# Run a specific test
uv run pytest tests/unit/test_utils.py::test_sleep_waits_correct_milliseconds

# Type checking
uv run mypy src/

# Linting
uv run ruff check src/

# Add a new dependency
uv add <package-name>

# Add a dev dependency
uv add --dev <package-name>

# Remove a dependency
uv remove <package-name>

# Update dependencies
uv lock --upgrade

# Install specific Python version
uv python install 3.10
```

## Architecture

The project follows a layered architecture with clear separation of concerns and dependency injection:

### Layer Structure

**Controllers** (`src/lol_replay_recorder/controllers/`)
- `LeagueReplayClient` - Primary interface for replay control via Riot's Replay API (port 2999)
  - Manages replay playback, recording, and rendering properties
  - Handles camera focusing on specific summoners
  - Provides async methods for all replay operations
- `LeagueClient` - High-level interface for League Client operations
  - Manages game settings, locale, and configuration
  - Integrates with GameSettingsManager for configuration management
- `RiotGameClient` - Handles Riot Client authentication and operations
- `WindowHandler` - Low-level keyboard/mouse automation using pyautogui and pygetwindow
  - Maps custom Key enum to pyautogui key names
  - Focuses windows, sends keyboard input, and controls mouse

**Services** (`src/lol_replay_recorder/services/`)
- `config/` - Configuration management services
  - `editors/` - INI and YAML file editors implementing ConfigEditor protocol
  - `game_settings.py` - GameSettingsManager for League game configuration
- `process/` - Process management services
  - `platform.py` - PlatformResolver for cross-platform process handling
  - `manager.py` - ProcessManager for process lifecycle management

**Clients** (`src/lol_replay_recorder/clients/`)
- `http/` - HTTP client implementations
  - `base.py` - BaseHTTPClient with retry logic and error handling
  - `lcu.py` - LCUClient for League Client API authentication
  - `riot.py` - RiotAPIClient for Riot Replay API communication

**Domain Layer** (`src/lol_replay_recorder/domain/`)
- `entities/` - Core business entities
  - `summoner.py` - Summoner entity representing League of Legends players
- `types/` - Type definitions and data structures
  - `replay_types.py` - Replay data structures (RecordingProperties, RenderProperties, etc.)
  - `riot_types.py` - Platform IDs and region types
  - `locale.py` - League of Legends supported locales
  - `metadata_types.py` - Metadata type definitions
- `errors.py` - Domain-specific error classes

**Protocols** (`src/lol_replay_recorder/protocols/`)
- `config_editor.py` - ConfigEditor protocol for configuration file operations
- `http_client.py` - HttpClient protocol for HTTP client implementations
- `window_manager.py` - WindowManager protocol for window automation

**Legacy API Layer** (`src/lol_replay_recorder/apis/`)
- Backward compatibility layer with deprecation warnings
- Redirects to new services layer

### Dependency Flow

```
Controllers → Services → Clients → Domain
     ↓         ↓         ↓       ↓
```

### Key Patterns

**Protocol-Based Design**
- All major interfaces defined as protocols in `src/lol_replay_recorder/protocols/`
- Services implement protocols for testability and flexibility
- Enables dependency injection and mocking

**Domain-Driven Structure**
- Pure domain objects in `domain/` layer with no external dependencies
- Clear separation between business logic and infrastructure
- Type definitions centralized in `domain/types/`

**Configuration Management**
- GameSettingsManager provides unified interface to game configuration
- Multiple editor types (INI, YAML) implementing ConfigEditor protocol
- Factory pattern for editor selection

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
- `tests/unit/domain/` - Tests for domain entities and types
- `tests/unit/protocols/` - Tests for protocol implementations
- `tests/unit/services/` - Tests for service layer components
- `tests/unit/controllers/` - Tests for controller layer
- `tests/e2e/` - End-to-end tests requiring League client (marked with `@pytest.mark.e2e`)
- Tests use `@pytest.mark.asyncio` for async functions
- Async mode is set to "auto" in pyproject.toml

### Migration to New Architecture

**Phase 4 Implementation Complete:**
- ✅ Created protocol interfaces for HttpClient, ConfigEditor, and WindowManager
- ✅ Moved models to domain structure (`domain/entities/`, `domain/types/`)
- ✅ Updated all import paths to use new domain structure
- ✅ Maintained backward compatibility in `models/__init__.py` with deprecation warnings
- ✅ Updated configuration editors to implement ConfigEditor protocol
- ✅ Added comprehensive tests for new structure

**Backward Compatibility:**
- Legacy imports from `lol_replay_recorder.models` still work with deprecation warnings
- Legacy APIs in `lol_replay_recorder.apis` redirect to new services
- All existing code continues to function while encouraging migration

### Important Notes

- All HTTP clients disable SSL verification due to Riot's self-signed certificates
- The replay API runs on localhost:2999 when a replay is active
- LCU API port is dynamic, read from lockfile each time
- Window automation requires the League client window to be focused and visible
- Player positions map to keyboard keys: 1-5 for ORDER team, Q-T for CHAOS team (indices 0-9)

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
