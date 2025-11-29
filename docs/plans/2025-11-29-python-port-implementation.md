# LoL Replay Recorder Python Port Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Port the TypeScript LoL Replay Recorder library to Python as an independent PyPI package

**Architecture:** Class-based structure mirroring TypeScript original, asyncio for async operations, httpx for HTTP requests, pyautogui/pygetwindow for window automation

**Tech Stack:** Python 3.10+, Poetry, uv, pytest, httpx, PyYAML, pyautogui, pygetwindow, pywin32

---

## Phase 1: Project Foundation

### Task 1: Initialize Project Structure

**Files:**
- Create: `pyproject.toml`
- Create: `src/lol_replay_recorder/__init__.py`
- Create: `README.md`
- Create: `.gitignore`

**Step 1: Create project root directory structure**

```bash
mkdir -p lol-replay-recorder-py
cd lol-replay-recorder-py
mkdir -p src/lol_replay_recorder/{controllers,models,apis,utils}
mkdir -p tests/{unit,e2e}/{apis,controllers}
mkdir -p docs/plans
```

**Step 2: Write pyproject.toml**

Create: `pyproject.toml`

```toml
[project]
name = "lol-replay-recorder"
version = "0.1.0"
description = "A Python library to record League of Legends replays"
authors = [{name = "wooto"}]
readme = "README.md"
requires-python = ">=3.10"
license = {text = "MIT"}

dependencies = [
    "httpx>=0.27.0",
    "PyYAML>=6.0",
    "pyautogui>=0.9.54",
    "pygetwindow>=0.0.9",
    "pywin32>=306; platform_system=='Windows'",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.23.0",
    "pytest-mock>=3.12.0",
    "mypy>=1.8.0",
    "ruff>=0.1.0",
]

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"

[tool.poetry]
packages = [{include = "lol_replay_recorder", from = "src"}]

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
markers = [
    "e2e: End-to-end tests requiring League client",
    "unit: Unit tests",
]

[tool.mypy]
python_version = "3.10"
strict = true
warn_return_any = true

[tool.ruff]
line-length = 100
target-version = "py310"
```

**Step 3: Create .gitignore**

Create: `.gitignore`

```
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
.pytest_cache/
.mypy_cache/
.ruff_cache/
venv/
ENV/
.venv/
```

**Step 4: Initialize git repository**

```bash
git init
git add .
git commit -m "chore: initialize Python port project structure"
```

---

### Task 2: Utility Functions Module

**Files:**
- Create: `src/lol_replay_recorder/utils/__init__.py`
- Create: `src/lol_replay_recorder/utils/utils.py`
- Create: `tests/unit/test_utils.py`

**Step 1: Write failing test for sleep functions**

Create: `tests/unit/test_utils.py`

```python
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
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/unit/test_utils.py -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'lol_replay_recorder'"

**Step 3: Write minimal implementation**

Create: `src/lol_replay_recorder/utils/__init__.py`

```python
from .utils import (
    sleep,
    sleep_in_seconds,
    millis_to_seconds,
    seconds_to_millis,
    convert_seconds_to_hms,
    format_date,
    convert_file_path,
    refine_region,
)

__all__ = [
    "sleep",
    "sleep_in_seconds",
    "millis_to_seconds",
    "seconds_to_millis",
    "convert_seconds_to_hms",
    "format_date",
    "convert_file_path",
    "refine_region",
]
```

Create: `src/lol_replay_recorder/utils/utils.py`

```python
import asyncio
import re
from datetime import datetime
from typing import Any


async def sleep(ms: int | float) -> None:
    """Sleep for specified milliseconds."""
    if ms <= 0:
        return
    await asyncio.sleep(ms / 1000)


async def sleep_in_seconds(s: int | float) -> None:
    """Sleep for specified seconds."""
    if s <= 0:
        return
    await asyncio.sleep(s)


def millis_to_seconds(ms: int | float) -> float:
    """Convert milliseconds to seconds."""
    return ms * 0.001


def seconds_to_millis(s: int | float) -> float:
    """Convert seconds to milliseconds."""
    return s * 1000


def convert_seconds_to_hms(s: float) -> str:
    """Format seconds in a nicely formatted string (e.g., '1h 23m 45s')."""
    seconds = round(s)
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    remaining_seconds = seconds % 60

    parts = []
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")
    if remaining_seconds > 0 or len(parts) == 0:
        parts.append(f"{remaining_seconds}s")

    return " ".join(parts)


def format_date(raw_date: Any) -> str:
    """Returns a new datetime in YYYY-MM-DD format."""
    if isinstance(raw_date, datetime):
        return raw_date.date().isoformat()
    return datetime.fromisoformat(str(raw_date)).date().isoformat()


def convert_file_path(path: str) -> str:
    """Replace forward slashes in file path with back slashes (Windows)."""
    return path.replace("/", "\\")


def refine_region(region: str) -> str:
    """Remove digits from region string."""
    return re.sub(r"\d", "", region)
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/unit/test_utils.py -v`
Expected: PASS

**Step 5: Add more utility function tests**

Append to: `tests/unit/test_utils.py`

```python
from lol_replay_recorder.utils.utils import (
    convert_seconds_to_hms,
    format_date,
    convert_file_path,
    refine_region,
    millis_to_seconds,
    seconds_to_millis,
)
from datetime import datetime


def test_convert_seconds_to_hms_with_hours():
    assert convert_seconds_to_hms(3661) == "1h 1m 1s"


def test_convert_seconds_to_hms_with_minutes_only():
    assert convert_seconds_to_hms(125) == "2m 5s"


def test_convert_seconds_to_hms_with_seconds_only():
    assert convert_seconds_to_hms(45) == "45s"


def test_convert_seconds_to_hms_with_zero():
    assert convert_seconds_to_hms(0) == "0s"


def test_format_date():
    date = datetime(2025, 11, 29, 15, 30)
    assert format_date(date) == "2025-11-29"


def test_convert_file_path():
    assert convert_file_path("C:/Riot Games/LoL") == "C:\\Riot Games\\LoL"


def test_refine_region():
    assert refine_region("na1") == "na"
    assert refine_region("euw1") == "euw"
    assert refine_region("kr") == "kr"


def test_millis_to_seconds():
    assert millis_to_seconds(1000) == 1.0
    assert millis_to_seconds(500) == 0.5


def test_seconds_to_millis():
    assert seconds_to_millis(1) == 1000
    assert seconds_to_millis(0.5) == 500
```

**Step 6: Run tests to verify they pass**

Run: `pytest tests/unit/test_utils.py -v`
Expected: ALL PASS

**Step 7: Commit**

```bash
git add src/lol_replay_recorder/utils/ tests/unit/test_utils.py
git commit -m "feat: add utility functions module with sleep and conversion helpers"
```

---

### Task 3: Custom Error Class

**Files:**
- Create: `src/lol_replay_recorder/models/__init__.py`
- Create: `src/lol_replay_recorder/models/custom_error.py`
- Create: `tests/unit/test_custom_error.py`

**Step 1: Write failing test**

Create: `tests/unit/test_custom_error.py`

```python
import pytest
from lol_replay_recorder.models.custom_error import CustomError


def test_custom_error_inherits_from_exception():
    assert issubclass(CustomError, Exception)


def test_custom_error_with_message():
    error = CustomError("Test error message")
    assert str(error) == "Test error message"


def test_custom_error_with_multiple_args():
    error = CustomError("Error", "arg1", "arg2")
    assert str(error) == "Error"
    assert error.args == ("Error", "arg1", "arg2")


def test_custom_error_can_be_raised():
    with pytest.raises(CustomError) as exc_info:
        raise CustomError("Test error")
    assert str(exc_info.value) == "Test error"
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/unit/test_custom_error.py -v`
Expected: FAIL with "ModuleNotFoundError"

**Step 3: Write minimal implementation**

Create: `src/lol_replay_recorder/models/__init__.py`

```python
from .custom_error import CustomError

__all__ = ["CustomError"]
```

Create: `src/lol_replay_recorder/models/custom_error.py`

```python
class CustomError(Exception):
    """Custom exception class for LoL Replay Recorder."""

    def __init__(self, *args):
        super().__init__(*args)
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/unit/test_custom_error.py -v`
Expected: ALL PASS

**Step 5: Commit**

```bash
git add src/lol_replay_recorder/models/ tests/unit/test_custom_error.py
git commit -m "feat: add CustomError exception class"
```

---

## Phase 2: Type Definitions and Models

### Task 4: Locale Enum

**Files:**
- Modify: `src/lol_replay_recorder/models/__init__.py`
- Create: `src/lol_replay_recorder/models/locale.py`
- Create: `tests/unit/test_locale.py`

**Step 1: Write failing test**

Create: `tests/unit/test_locale.py`

```python
from lol_replay_recorder.models.locale import Locale


def test_locale_has_korean():
    assert Locale.ko_KR == "ko_KR"


def test_locale_has_english_us():
    assert Locale.en_US == "en_US"


def test_locale_has_japanese():
    assert Locale.ja_JP == "ja_JP"


def test_locale_values_are_strings():
    assert isinstance(Locale.ko_KR.value, str)


def test_locale_has_all_expected_locales():
    expected_locales = {
        "ja_JP", "ko_KR", "ar_AE", "cs_CZ", "de_DE", "el_GR",
        "en_AU", "en_GB", "en_PH", "en_SG", "en_US",
        "es_AR", "es_ES", "es_MX", "fr_FR", "hu_HU", "it_IT",
        "pl_PL", "pt_BR", "ro_RO", "ru_RU", "th_TH", "tr_TR",
        "vi_VN", "zh_MY", "zh_TW"
    }
    actual_locales = {locale.value for locale in Locale}
    assert actual_locales == expected_locales
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/unit/test_locale.py -v`
Expected: FAIL with "ModuleNotFoundError"

**Step 3: Write minimal implementation**

Create: `src/lol_replay_recorder/models/locale.py`

```python
from enum import Enum


class Locale(str, Enum):
    """League of Legends supported locales."""

    ja_JP = "ja_JP"
    ko_KR = "ko_KR"
    ar_AE = "ar_AE"
    cs_CZ = "cs_CZ"
    de_DE = "de_DE"
    el_GR = "el_GR"
    en_AU = "en_AU"
    en_GB = "en_GB"
    en_PH = "en_PH"
    en_SG = "en_SG"
    en_US = "en_US"
    es_AR = "es_AR"
    es_ES = "es_ES"
    es_MX = "es_MX"
    fr_FR = "fr_FR"
    hu_HU = "hu_HU"
    it_IT = "it_IT"
    pl_PL = "pl_PL"
    pt_BR = "pt_BR"
    ro_RO = "ro_RO"
    ru_RU = "ru_RU"
    th_TH = "th_TH"
    tr_TR = "tr_TR"
    vi_VN = "vi_VN"
    zh_MY = "zh_MY"
    zh_TW = "zh_TW"
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/unit/test_locale.py -v`
Expected: ALL PASS

**Step 5: Update models __init__.py**

Modify: `src/lol_replay_recorder/models/__init__.py`

```python
from .custom_error import CustomError
from .locale import Locale

__all__ = ["CustomError", "Locale"]
```

**Step 6: Commit**

```bash
git add src/lol_replay_recorder/models/locale.py tests/unit/test_locale.py src/lol_replay_recorder/models/__init__.py
git commit -m "feat: add Locale enum with all supported LoL locales"
```

---

### Task 5: Riot Types

**Files:**
- Modify: `src/lol_replay_recorder/models/__init__.py`
- Create: `src/lol_replay_recorder/models/riot_types.py`
- Create: `tests/unit/test_riot_types.py`

**Step 1: Write failing test**

Create: `tests/unit/test_riot_types.py`

```python
from lol_replay_recorder.models.riot_types import PlatformId, Region, Cluster


def test_platform_id_enum_has_na1():
    assert PlatformId.NA1 == "na1"


def test_platform_id_enum_has_kr():
    assert PlatformId.KR == "kr"


def test_region_type_allows_valid_regions():
    # These should be valid Region types
    region: Region = "na1"
    assert region == "na1"


def test_cluster_type_allows_valid_clusters():
    # These should be valid Cluster types
    cluster: Cluster = "americas"
    assert cluster == "americas"
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/unit/test_riot_types.py -v`
Expected: FAIL with "ModuleNotFoundError"

**Step 3: Write minimal implementation**

Create: `src/lol_replay_recorder/models/riot_types.py`

```python
from enum import Enum
from typing import Literal


class PlatformId(str, Enum):
    """Riot platform IDs for different regions."""

    EUW1 = "euw1"
    EUNE1 = "eun1"
    NA1 = "na1"
    LA1 = "la1"
    LA2 = "la2"
    KR = "kr"
    JP1 = "jp1"
    BR1 = "br1"
    OC1 = "oc1"
    RU = "ru"
    TR1 = "tr1"
    EUROPE = "europe"
    ASIA = "asia"
    SEA = "sea"
    AMERICAS = "americas"
    AP = "ap"
    BR = "br"
    EU = "eu"
    NA = "na"
    LATAM = "latam"
    PH2 = "ph2"
    SG2 = "sg2"
    TH2 = "th2"
    TW2 = "tw2"
    VN2 = "vn2"
    ESPORTS = "esports"
    APAC = "apac"


# Type aliases for specific platform categories
Cluster = Literal[
    "europe",
    "americas",
    "asia",
    "sea",
    "esports",
]

Region = Literal[
    "br1",
    "eun1",
    "euw1",
    "jp1",
    "kr",
    "la1",
    "la2",
    "na1",
    "oc1",
    "ru",
    "tr1",
    "ph2",
    "sg2",
    "th2",
    "tw2",
    "vn2",
]
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/unit/test_riot_types.py -v`
Expected: ALL PASS

**Step 5: Update models __init__.py**

Modify: `src/lol_replay_recorder/models/__init__.py`

```python
from .custom_error import CustomError
from .locale import Locale
from .riot_types import PlatformId, Region, Cluster

__all__ = ["CustomError", "Locale", "PlatformId", "Region", "Cluster"]
```

**Step 6: Commit**

```bash
git add src/lol_replay_recorder/models/riot_types.py tests/unit/test_riot_types.py src/lol_replay_recorder/models/__init__.py
git commit -m "feat: add Riot platform IDs and region types"
```

---

### Task 6: Replay Type Definitions

**Files:**
- Modify: `src/lol_replay_recorder/models/__init__.py`
- Create: `src/lol_replay_recorder/models/replay_type.py`
- Create: `tests/unit/test_replay_type.py`

**Step 1: Write failing test**

Create: `tests/unit/test_replay_type.py`

```python
from lol_replay_recorder.models.replay_type import (
    RecordingProperties,
    RenderProperties,
    GameData,
)


def test_recording_properties_structure():
    props: RecordingProperties = {
        "codec": "x264",
        "currentTime": 100.0,
        "endTime": 200.0,
        "enforceFrameRate": True,
        "framesPerSecond": 60,
        "height": 1080,
        "lossless": False,
        "path": "/path/to/recording",
        "recording": True,
        "replaySpeed": 1.0,
        "startTime": 0.0,
        "width": 1920,
    }
    assert props["codec"] == "x264"
    assert props["recording"] is True


def test_render_properties_has_selection_name():
    props: RenderProperties = {
        "selectionName": "Player1",
        "banners": True,
        "cameraAttached": False,
        # ... minimal required fields
    }
    assert props["selectionName"] == "Player1"
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/unit/test_replay_type.py -v`
Expected: FAIL with "ModuleNotFoundError"

**Step 3: Write minimal implementation**

Create: `src/lol_replay_recorder/models/replay_type.py`

```python
from typing import TypedDict, Any


class Vector3(TypedDict):
    """3D vector coordinates."""
    x: float
    y: float
    z: float


class ColorRGBA(TypedDict):
    """RGBA color."""
    r: float
    g: float
    b: float
    a: float


class RecordingProperties(TypedDict):
    """Replay recording properties."""
    codec: str
    currentTime: float
    endTime: float
    enforceFrameRate: bool
    framesPerSecond: int
    height: int
    lossless: bool
    path: str
    recording: bool
    replaySpeed: float
    startTime: float
    width: int


class RenderProperties(TypedDict, total=False):
    """Replay render properties."""
    banners: bool
    cameraAttached: bool
    cameraLookSpeed: float
    cameraMode: str
    cameraMoveSpeed: float
    cameraPosition: Vector3
    cameraRotation: Vector3
    characters: bool
    depthFogColor: ColorRGBA
    depthFogEnabled: bool
    depthFogEnd: float
    depthFogIntensity: float
    depthFogStart: float
    depthOfFieldCircle: float
    depthOfFieldDebug: bool
    depthOfFieldEnabled: bool
    depthOfFieldFar: float
    depthOfFieldMid: float
    depthOfFieldNear: float
    depthOfFieldWidth: float
    environment: bool
    farClip: float
    fieldOfView: float
    floatingText: bool
    fogOfWar: bool
    healthBarChampions: bool
    healthBarMinions: bool
    healthBarPets: bool
    healthBarStructures: bool
    healthBarWards: bool
    heightFogColor: ColorRGBA
    heightFogEnabled: bool
    heightFogEnd: float
    heightFogIntensity: float
    heightFogStart: float
    interfaceAll: bool
    interfaceAnnounce: bool
    interfaceChat: bool
    interfaceFrames: bool
    interfaceKillCallouts: bool
    interfaceMinimap: bool
    interfaceNeutralTimers: bool
    interfaceQuests: bool | None
    interfaceReplay: bool
    interfaceScore: bool
    interfaceScoreboard: bool
    interfaceTarget: bool
    interfaceTimeline: bool
    navGridOffset: float
    nearClip: float
    outlineHover: bool
    outlineSelect: bool
    particles: bool
    selectionName: str
    selectionOffset: Vector3
    skyboxOffset: float
    skyboxPath: str
    skyboxRadius: float
    skyboxRotation: float
    sunDirection: Vector3


class Item(TypedDict):
    """Player item."""
    canUse: bool
    consumable: bool
    count: int
    displayName: str
    itemID: int
    price: int
    rawDescription: str
    rawDisplayName: str
    slot: int


class Keystone(TypedDict):
    """Rune keystone."""
    displayName: str
    id: int
    rawDescription: str
    rawDisplayName: str


class RuneTree(TypedDict):
    """Rune tree."""
    displayName: str
    id: int
    rawDescription: str
    rawDisplayName: str


class Runes(TypedDict):
    """Player runes."""
    keystone: Keystone
    primaryRuneTree: RuneTree
    secondaryRuneTree: RuneTree


class Scores(TypedDict):
    """Player scores."""
    assists: int
    creepScore: int
    deaths: int
    kills: int
    wardScore: float


class SummonerSpell(TypedDict):
    """Summoner spell."""
    displayName: str
    rawDescription: str
    rawDisplayName: str


class SummonerSpells(TypedDict):
    """Player summoner spells."""
    summonerSpellOne: SummonerSpell
    summonerSpellTwo: SummonerSpell


class Player(TypedDict):
    """Game player data."""
    championName: str
    isBot: bool
    isDead: bool
    items: list[Item]
    level: int
    riotIdGameName: str
    position: str
    rawChampionName: str
    rawSkinName: str
    respawnTimer: float
    runes: Runes
    scores: Scores
    screenPositionBottom: str
    screenPositionCenter: str
    skinID: int
    skinName: str
    summonerName: str
    summonerSpells: SummonerSpells
    team: str


class Event(TypedDict, total=False):
    """Game event."""
    EventID: int
    EventName: str
    EventTime: float
    Assisters: list[str]
    KillerName: str
    VictimName: str
    KillStreak: int


class Events(TypedDict):
    """Game events container."""
    Events: list[Event]


class GameDetails(TypedDict):
    """Game details."""
    gameMode: str
    gameTime: float
    mapName: str
    mapNumber: int
    mapTerrain: str


class ActivePlayer(TypedDict):
    """Active player info."""
    error: str


class GameData(TypedDict):
    """Complete game data."""
    activePlayer: ActivePlayer
    allPlayers: list[Player]
    events: Events
    gameData: GameDetails
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/unit/test_replay_type.py -v`
Expected: ALL PASS

**Step 5: Update models __init__.py**

Modify: `src/lol_replay_recorder/models/__init__.py`

```python
from .custom_error import CustomError
from .locale import Locale
from .riot_types import PlatformId, Region, Cluster
from .replay_type import RecordingProperties, RenderProperties, GameData

__all__ = [
    "CustomError",
    "Locale",
    "PlatformId",
    "Region",
    "Cluster",
    "RecordingProperties",
    "RenderProperties",
    "GameData",
]
```

**Step 6: Commit**

```bash
git add src/lol_replay_recorder/models/replay_type.py tests/unit/test_replay_type.py src/lol_replay_recorder/models/__init__.py
git commit -m "feat: add replay type definitions for recording and rendering"
```

---

### Task 7: Summoner Model

**Files:**
- Modify: `src/lol_replay_recorder/models/__init__.py`
- Create: `src/lol_replay_recorder/models/summoner.py`
- Create: `tests/unit/test_summoner.py`

**Step 1: Write failing test**

Create: `tests/unit/test_summoner.py`

```python
from lol_replay_recorder.models.summoner import Summoner
from urllib.parse import quote


def test_summoner_initialization():
    summoner = Summoner("TestPlayer", "NA1", "puuid-123")
    assert summoner.summoner_name == "TestPlayer"
    assert summoner.tagline == "NA1"
    assert summoner.puuid == "puuid-123"


def test_summoner_riot_id_generation():
    summoner = Summoner("TestPlayer", "NA1")
    expected = f"{quote('TestPlayer')}#NA1"
    assert summoner.riot_id == expected


def test_summoner_with_special_characters_in_name():
    summoner = Summoner("Test Player!", "KR")
    assert "Test%20Player%21" in summoner.riot_id
    assert summoner.riot_id.endswith("#KR")


def test_summoner_default_puuid():
    summoner = Summoner("Player", "EUW")
    assert summoner.puuid == ""
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/unit/test_summoner.py -v`
Expected: FAIL with "ModuleNotFoundError"

**Step 3: Write minimal implementation**

Create: `src/lol_replay_recorder/models/summoner.py`

```python
from urllib.parse import quote


class Summoner:
    """Represents a League of Legends summoner."""

    def __init__(self, summoner_name: str, tagline: str, puuid: str = ""):
        self.summoner_name = summoner_name
        self.tagline = tagline
        self.riot_id = f"{quote(summoner_name)}#{tagline}"
        self.puuid = puuid
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/unit/test_summoner.py -v`
Expected: ALL PASS

**Step 5: Update models __init__.py**

Modify: `src/lol_replay_recorder/models/__init__.py`

```python
from .custom_error import CustomError
from .locale import Locale
from .riot_types import PlatformId, Region, Cluster
from .replay_type import RecordingProperties, RenderProperties, GameData
from .summoner import Summoner

__all__ = [
    "CustomError",
    "Locale",
    "PlatformId",
    "Region",
    "Cluster",
    "RecordingProperties",
    "RenderProperties",
    "GameData",
    "Summoner",
]
```

**Step 6: Commit**

```bash
git add src/lol_replay_recorder/models/summoner.py tests/unit/test_summoner.py src/lol_replay_recorder/models/__init__.py
git commit -m "feat: add Summoner model with riot ID generation"
```

---

## Phase 3: Configuration File Editors

### Task 8: INI Editor

**Files:**
- Create: `src/lol_replay_recorder/apis/__init__.py`
- Create: `src/lol_replay_recorder/apis/ini_editor.py`
- Create: `tests/unit/apis/test_ini_editor.py`

**Step 1: Write failing test**

Create: `tests/unit/apis/test_ini_editor.py`

```python
import pytest
from pathlib import Path
from lol_replay_recorder.apis.ini_editor import IniEditor


@pytest.fixture
def temp_ini_file(tmp_path):
    """Create a temporary INI file for testing."""
    ini_content = """[General]
EnableReplayApi=1
GameMouseSpeed=10

[HUD]
ShowTimestamps=1
"""
    ini_file = tmp_path / "test.ini"
    ini_file.write_text(ini_content)
    return str(ini_file)


def test_ini_editor_loads_file(temp_ini_file):
    editor = IniEditor(temp_ini_file)
    assert editor.filename == temp_ini_file
    assert "General" in editor.data
    assert editor.data["General"]["EnableReplayApi"] == "1"


def test_ini_editor_update_section(temp_ini_file):
    editor = IniEditor(temp_ini_file)
    editor.update_section("General", "EnableReplayApi", "0")
    assert editor.data["General"]["EnableReplayApi"] == "0"


def test_ini_editor_create_new_section(temp_ini_file):
    editor = IniEditor(temp_ini_file)
    editor.update_section("NewSection", "NewKey", "NewValue")
    assert "NewSection" in editor.data
    assert editor.data["NewSection"]["NewKey"] == "NewValue"


def test_ini_editor_save(temp_ini_file):
    editor = IniEditor(temp_ini_file)
    editor.update_section("General", "EnableReplayApi", "0")
    editor.save()

    # Read file and verify changes
    editor2 = IniEditor(temp_ini_file)
    assert editor2.data["General"]["EnableReplayApi"] == "0"


def test_ini_editor_handles_nonexistent_file():
    with pytest.raises(Exception) as exc_info:
        IniEditor("/nonexistent/path/file.ini")
    assert "Failed to load INI file" in str(exc_info.value)
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/unit/apis/test_ini_editor.py -v`
Expected: FAIL with "ModuleNotFoundError"

**Step 3: Write minimal implementation**

Create: `src/lol_replay_recorder/apis/__init__.py`

```python
from .ini_editor import IniEditor
from .yaml_editor import YamlEditor

__all__ = ["IniEditor", "YamlEditor"]
```

Create: `src/lol_replay_recorder/apis/ini_editor.py`

```python
import configparser
from pathlib import Path
from typing import Any


class IniEditor:
    """Editor for INI configuration files."""

    def __init__(self, filename: str):
        self.filename = filename
        self.data = self._load_ini()

    def _load_ini(self) -> dict[str, dict[str, Any]]:
        """Load INI file and return as nested dict."""
        try:
            config = configparser.ConfigParser()
            config.read(self.filename)
            # Convert to dict for easier manipulation
            return {section: dict(config[section]) for section in config.sections()}
        except Exception as e:
            raise Exception(f"Failed to load INI file: {str(e)}")

    def save(self) -> None:
        """Save current data back to INI file."""
        config = configparser.ConfigParser()
        for section, values in self.data.items():
            config[section] = values

        with open(self.filename, "w", encoding="utf-8") as f:
            config.write(f, space_around_delimiters=False)

    def update_section(self, section: str, key: str, value: Any) -> None:
        """Update or create a section with key-value pair."""
        if section not in self.data:
            self.data[section] = {}
        self.data[section][key] = str(value)
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/unit/apis/test_ini_editor.py -v`
Expected: ALL PASS

**Step 5: Commit**

```bash
git add src/lol_replay_recorder/apis/ tests/unit/apis/test_ini_editor.py
git commit -m "feat: add IniEditor for managing INI config files"
```

---

### Task 9: YAML Editor

**Files:**
- Modify: `src/lol_replay_recorder/apis/__init__.py`
- Create: `src/lol_replay_recorder/apis/yaml_editor.py`
- Create: `tests/unit/apis/test_yaml_editor.py`

**Step 1: Write failing test**

Create: `tests/unit/apis/test_yaml_editor.py`

```python
import pytest
from pathlib import Path
from lol_replay_recorder.apis.yaml_editor import YamlEditor


@pytest.fixture
def temp_yaml_file(tmp_path):
    """Create a temporary YAML file for testing."""
    yaml_content = """locale_data:
  default_locale: en_US
  available_locales:
    - en_US
    - ko_KR
    - ja_JP
settings:
  locale: en_US
  region: na1
"""
    yaml_file = tmp_path / "test.yaml"
    yaml_file.write_text(yaml_content)
    return str(yaml_file)


def test_yaml_editor_loads_file(temp_yaml_file):
    editor = YamlEditor(temp_yaml_file)
    assert editor.filename == temp_yaml_file
    assert "locale_data" in editor.data
    assert editor.data["locale_data"]["default_locale"] == "en_US"


def test_yaml_editor_update_nested_path(temp_yaml_file):
    editor = YamlEditor(temp_yaml_file)
    editor.update("locale_data.default_locale", "ko_KR")
    assert editor.data["locale_data"]["default_locale"] == "ko_KR"


def test_yaml_editor_update_creates_missing_keys(temp_yaml_file):
    editor = YamlEditor(temp_yaml_file)
    editor.update("new_section.new_key", "new_value")
    assert editor.data["new_section"]["new_key"] == "new_value"


def test_yaml_editor_save_changes(temp_yaml_file):
    editor = YamlEditor(temp_yaml_file)
    editor.update("settings.locale", "ja_JP")
    editor.save_changes()

    # Read file and verify changes
    editor2 = YamlEditor(temp_yaml_file)
    assert editor2.data["settings"]["locale"] == "ja_JP"


def test_yaml_editor_handles_nonexistent_file():
    with pytest.raises(Exception) as exc_info:
        YamlEditor("/nonexistent/path/file.yaml")
    assert "Failed to load YAML file" in str(exc_info.value)
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/unit/apis/test_yaml_editor.py -v`
Expected: FAIL with "ModuleNotFoundError"

**Step 3: Write minimal implementation**

Create: `src/lol_replay_recorder/apis/yaml_editor.py`

```python
import yaml
from typing import Any


class YamlEditor:
    """Editor for YAML configuration files."""

    def __init__(self, filename: str):
        self.filename = filename
        self.data = self._load_yaml()

    def _load_yaml(self) -> dict[str, Any]:
        """Load YAML file and return as dict."""
        try:
            with open(self.filename, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            raise Exception(f"Failed to load YAML file: {str(e)}")

    def _save_yaml(self) -> None:
        """Save current data back to YAML file."""
        try:
            with open(self.filename, "w", encoding="utf-8") as f:
                yaml.dump(self.data, f, default_flow_style=False, allow_unicode=True)
            print(f"YAML file saved to {self.filename}")
        except Exception as e:
            raise Exception(f"Failed to save YAML file: {str(e)}")

    def update(self, path: str, value: Any) -> None:
        """Update a nested value using dot notation path."""
        keys = path.split(".")
        current = self.data

        for i, key in enumerate(keys[:-1]):
            if key not in current:
                current[key] = {}
            current = current[key]

        current[keys[-1]] = value

    def save_changes(self) -> None:
        """Save changes to file."""
        self._save_yaml()
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/unit/apis/test_yaml_editor.py -v`
Expected: ALL PASS

**Step 5: Commit**

```bash
git add src/lol_replay_recorder/apis/yaml_editor.py tests/unit/apis/test_yaml_editor.py
git commit -m "feat: add YamlEditor for managing YAML config files"
```

---

## Phase 4: HTTP Request Modules

### Task 10: Riot Request (Replay API)

**Files:**
- Create: `src/lol_replay_recorder/models/riot_request.py`
- Create: `tests/unit/test_riot_request.py`

**Step 1: Write failing test**

Create: `tests/unit/test_riot_request.py`

```python
import pytest
from unittest.mock import AsyncMock, patch
from lol_replay_recorder.models.riot_request import make_request
from lol_replay_recorder.models.custom_error import CustomError


@pytest.mark.asyncio
async def test_make_request_success():
    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.json = AsyncMock(return_value={"data": "test"})

    with patch("httpx.AsyncClient.request", return_value=mock_response):
        result = await make_request("GET", "https://127.0.0.1:2999/test")
        assert result == {"data": "test"}


@pytest.mark.asyncio
async def test_make_request_404_raises_custom_error():
    mock_response = AsyncMock()
    mock_response.status_code = 404
    mock_response.is_success = False

    with patch("httpx.AsyncClient.request", return_value=mock_response):
        with pytest.raises(CustomError) as exc_info:
            await make_request("GET", "https://127.0.0.1:2999/test", retries=0)
        assert "Failed to find the requested resource" in str(exc_info.value)


@pytest.mark.asyncio
async def test_make_request_retries_on_failure():
    mock_response = AsyncMock()
    mock_response.status_code = 500
    mock_response.is_success = False

    with patch("httpx.AsyncClient.request", return_value=mock_response) as mock_req:
        with pytest.raises(Exception):
            await make_request("GET", "https://127.0.0.1:2999/test", retries=2)
        # Should retry 2 times + initial = 3 total calls
        assert mock_req.call_count >= 2
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/unit/test_riot_request.py -v`
Expected: FAIL with "ModuleNotFoundError"

**Step 3: Write minimal implementation**

Create: `src/lol_replay_recorder/models/riot_request.py`

```python
import httpx
import ssl
from typing import Any
from .custom_error import CustomError


async def make_request(
    method: str,
    url: str,
    headers: dict[str, str] | None = None,
    body: dict[str, Any] | None = None,
    retries: int = 5,
) -> Any:
    """
    Make HTTP request to Riot Replay API.
    The replay API uses self-signed certificates, so we disable SSL verification.
    """
    if retries < 0:
        raise Exception("Client Request Error: Max retries exceeded")

    new_headers = {**(headers or {}), "Content-Type": "application/json"}

    try:
        async with httpx.AsyncClient(verify=False) as client:
            response = await client.request(
                method=method,
                url=url,
                headers=new_headers,
                json=body if method.upper() != "GET" else None,
            )

            if not response.is_success:
                if response.status_code == 404:
                    raise CustomError("Failed to find the requested resource.")
                return await make_request(method, url, headers, body, retries - 1)

            try:
                return response.json()
            except Exception:
                return response

    except CustomError:
        raise
    except Exception as e:
        if retries <= 0:
            raise Exception(f"Client Request Error: {url}, {str(e)}")
        return await make_request(method, url, headers, body, retries - 1)
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/unit/test_riot_request.py -v`
Expected: ALL PASS

**Step 5: Update models __init__.py**

Modify: `src/lol_replay_recorder/models/__init__.py`

```python
from .custom_error import CustomError
from .locale import Locale
from .riot_types import PlatformId, Region, Cluster
from .replay_type import RecordingProperties, RenderProperties, GameData
from .summoner import Summoner
from .riot_request import make_request

__all__ = [
    "CustomError",
    "Locale",
    "PlatformId",
    "Region",
    "Cluster",
    "RecordingProperties",
    "RenderProperties",
    "GameData",
    "Summoner",
    "make_request",
]
```

**Step 6: Commit**

```bash
git add src/lol_replay_recorder/models/riot_request.py tests/unit/test_riot_request.py src/lol_replay_recorder/models/__init__.py
git commit -m "feat: add make_request for Riot Replay API with SSL bypass"
```

---

### Task 11: LCU Request (League Client API)

**Files:**
- Create: `src/lol_replay_recorder/models/lcu_request.py`
- Create: `tests/unit/test_lcu_request.py`

**Step 1: Write failing test**

Create: `tests/unit/test_lcu_request.py`

```python
import pytest
from unittest.mock import AsyncMock, patch, mock_open
from pathlib import Path
from lol_replay_recorder.models.lcu_request import (
    make_lcu_request,
    read_lockfile,
)


@pytest.mark.asyncio
async def test_read_lockfile_success():
    lockfile_content = "LeagueClient:12345:54321:mypassword:https"

    with patch("builtins.open", mock_open(read_data=lockfile_content)):
        result = await read_lockfile("/fake/path/lockfile")
        assert result["port"] == "54321"
        assert result["password"] == "mypassword"


@pytest.mark.asyncio
async def test_make_lcu_request_uses_lockfile_credentials():
    lockfile_content = "LeagueClient:12345:54321:mypassword:https"
    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.json = AsyncMock(return_value={"data": "test"})

    with patch("builtins.open", mock_open(read_data=lockfile_content)):
        with patch("httpx.AsyncClient.request", return_value=mock_response) as mock_req:
            result = await make_lcu_request(
                "/fake/lockfile",
                "/test/endpoint",
                "GET"
            )
            assert result == {"data": "test"}
            # Verify authorization header was set
            call_kwargs = mock_req.call_args.kwargs
            assert "Authorization" in call_kwargs["headers"]
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/unit/test_lcu_request.py -v`
Expected: FAIL with "ModuleNotFoundError"

**Step 3: Write minimal implementation**

Create: `src/lol_replay_recorder/models/lcu_request.py`

```python
import httpx
import base64
import asyncio
from pathlib import Path
from typing import Any


async def read_lockfile(lockfile_path: str) -> dict[str, str]:
    """
    Read League Client lockfile and extract credentials.
    Format: LeagueClient:PID:PORT:PASSWORD:PROTOCOL
    """
    # Wait for lockfile to exist
    path = Path(lockfile_path)
    timeout = 60  # seconds
    elapsed = 0

    while not path.exists() and elapsed < timeout:
        await asyncio.sleep(1)
        elapsed += 1

    if not path.exists():
        raise FileNotFoundError(f"Lockfile not found: {lockfile_path}")

    content = path.read_text(encoding="utf-8")
    parts = content.split(":")

    return {
        "port": parts[2],
        "password": parts[3],
    }


async def make_lcu_request(
    lockfile_path: str,
    endpoint: str,
    method: str = "GET",
    body: dict[str, Any] | None = None,
    retries: int = 3,
) -> Any:
    """
    Make authenticated request to League Client Update (LCU) API.
    Uses credentials from lockfile.
    """
    credentials = await read_lockfile(lockfile_path)
    port = credentials["port"]
    password = credentials["password"]

    # Create basic auth header
    auth_string = f"riot:{password}"
    auth_bytes = auth_string.encode("utf-8")
    auth_b64 = base64.b64encode(auth_bytes).decode("utf-8")

    url = f"https://127.0.0.1:{port}{endpoint}"
    headers = {
        "Authorization": f"Basic {auth_b64}",
        "Content-Type": "application/json",
    }

    try:
        async with httpx.AsyncClient(verify=False) as client:
            response = await client.request(
                method=method,
                url=url,
                headers=headers,
                json=body if method.upper() != "GET" else None,
            )

            if not response.is_success:
                if retries <= 0:
                    raise Exception(
                        f"LCU Request Error: {response.status_code} {response.reason_phrase}"
                    )
                return await make_lcu_request(
                    lockfile_path, endpoint, method, body, retries - 1
                )

            try:
                return response.json()
            except Exception:
                return response

    except Exception as e:
        if retries <= 0:
            raise Exception(f"LCU Request Error: {url}, {str(e)}")
        return await make_lcu_request(
            lockfile_path, endpoint, method, body, retries - 1
        )
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/unit/test_lcu_request.py -v`
Expected: ALL PASS

**Step 5: Update models __init__.py**

Modify: `src/lol_replay_recorder/models/__init__.py`

```python
from .custom_error import CustomError
from .locale import Locale
from .riot_types import PlatformId, Region, Cluster
from .replay_type import RecordingProperties, RenderProperties, GameData
from .summoner import Summoner
from .riot_request import make_request
from .lcu_request import make_lcu_request, read_lockfile

__all__ = [
    "CustomError",
    "Locale",
    "PlatformId",
    "Region",
    "Cluster",
    "RecordingProperties",
    "RenderProperties",
    "GameData",
    "Summoner",
    "make_request",
    "make_lcu_request",
    "read_lockfile",
]
```

**Step 6: Commit**

```bash
git add src/lol_replay_recorder/models/lcu_request.py tests/unit/test_lcu_request.py src/lol_replay_recorder/models/__init__.py
git commit -m "feat: add make_lcu_request for League Client API with lockfile auth"
```

---

## Phase 5: Window Automation

### Task 12: Window Handler with pyautogui

**Files:**
- Create: `src/lol_replay_recorder/controllers/__init__.py`
- Create: `src/lol_replay_recorder/controllers/window_handler.py`
- Create: `tests/unit/controllers/test_window_handler.py`

**Step 1: Write failing test**

Create: `tests/unit/controllers/test_window_handler.py`

```python
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
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/unit/controllers/test_window_handler.py -v`
Expected: FAIL with "ModuleNotFoundError"

**Step 3: Write minimal implementation**

Create: `src/lol_replay_recorder/controllers/__init__.py`

```python
from .window_handler import WindowHandler, Key, Region

__all__ = ["WindowHandler", "Key", "Region"]
```

Create: `src/lol_replay_recorder/controllers/window_handler.py`

```python
import asyncio
from enum import IntEnum
import pyautogui
import pygetwindow as gw
from typing import Any


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
        await asyncio.to_thread(pyautogui.press, key_name)

    async def press_key(self, key: Key) -> None:
        """Press a key."""
        await self.keyboard_type(key)

    async def mouse_move(self, x: int, y: int) -> None:
        """Move mouse to coordinates."""
        await asyncio.to_thread(pyautogui.moveTo, x, y)

    async def mouse_left_click(self) -> None:
        """Perform left mouse click."""
        await asyncio.to_thread(pyautogui.click)

    async def focus_client_window(self, window_title: str, retry: int = 10) -> None:
        """Focus a window by title."""
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
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/unit/controllers/test_window_handler.py -v`
Expected: ALL PASS

**Step 5: Commit**

```bash
git add src/lol_replay_recorder/controllers/ tests/unit/controllers/test_window_handler.py
git commit -m "feat: add WindowHandler for keyboard/mouse automation with pyautogui"
```

---

## Phase 6: Core Controllers

### Task 13: League Replay Client

**Files:**
- Modify: `src/lol_replay_recorder/controllers/__init__.py`
- Create: `src/lol_replay_recorder/controllers/league_replay_client.py`
- Create: `tests/unit/controllers/test_league_replay_client.py`

**Step 1: Write failing test**

Create: `tests/unit/controllers/test_league_replay_client.py`

```python
import pytest
from unittest.mock import AsyncMock, patch
from lol_replay_recorder.controllers.league_replay_client import LeagueReplayClient


@pytest.mark.asyncio
async def test_league_replay_client_initialization():
    client = LeagueReplayClient()
    assert client.url == "https://127.0.0.1:2999"
    assert client.pid is None


@pytest.mark.asyncio
async def test_get_playback_properties():
    client = LeagueReplayClient()

    mock_response = {"time": 100.0, "paused": False}

    with patch("lol_replay_recorder.models.riot_request.make_request") as mock_req:
        mock_req.return_value = mock_response
        result = await client.get_playback_properties()
        assert result["time"] == 100.0
        mock_req.assert_called_once_with("GET", "https://127.0.0.1:2999/replay/playback")


@pytest.mark.asyncio
async def test_get_recording_properties():
    client = LeagueReplayClient()

    mock_response = {"recording": True, "currentTime": 50.0}

    with patch("lol_replay_recorder.models.riot_request.make_request") as mock_req:
        mock_req.return_value = mock_response
        result = await client.get_recording_properties()
        assert result["recording"] is True
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/unit/controllers/test_league_replay_client.py -v`
Expected: FAIL with "ModuleNotFoundError"

**Step 3: Write minimal implementation**

Create: `src/lol_replay_recorder/controllers/league_replay_client.py`

```python
import os
from typing import Any
from ..models.riot_request import make_request
from ..models.replay_type import RecordingProperties, RenderProperties, GameData
from ..models.custom_error import CustomError
from ..utils.utils import sleep_in_seconds
from .window_handler import WindowHandler, Key

# Disable SSL warnings for self-signed certs
os.environ["PYTHONHTTPSVERIFY"] = "0"


class LeagueReplayClient:
    """Client for interacting with League of Legends Replay API."""

    def __init__(self):
        self.url = "https://127.0.0.1:2999"
        self.pid: int | None = None

    async def init(self) -> None:
        """Initialize client by fetching process ID."""
        try:
            pid = await self.get_process_id()
            self.set_process_id(pid)
        except Exception as e:
            print(f"Error initializing replay client: {e}")

    def set_process_id(self, pid: int) -> None:
        """Set the replay process ID."""
        self.pid = pid

    async def get_process_id(self) -> int:
        """Get the replay process ID from the API."""
        if self.pid:
            return self.pid

        replay_data = await make_request("GET", f"{self.url}/replay/game")
        if replay_data and "processID" in replay_data:
            self.pid = replay_data["processID"]
        return self.pid

    async def exit(self) -> None:
        """Exit the replay by killing the process."""
        try:
            pid = await self.get_process_id()
            os.kill(pid, 9)  # SIGKILL
        except Exception:
            pass  # Silently ignore errors

    async def get_playback_properties(self) -> dict[str, Any]:
        """Get current playback properties."""
        return await make_request("GET", f"{self.url}/replay/playback")

    async def post_playback_properties(self, options: dict[str, Any]) -> dict[str, Any]:
        """Update playback properties."""
        return await make_request("POST", f"{self.url}/replay/playback", body=options)

    async def get_recording_properties(self) -> RecordingProperties:
        """Get current recording properties."""
        return await make_request("GET", f"{self.url}/replay/recording")

    async def post_recording_properties(self, options: dict[str, Any]) -> dict[str, Any]:
        """Update recording properties."""
        return await make_request("POST", f"{self.url}/replay/recording", body=options)

    async def get_render_properties(self) -> RenderProperties:
        """Get current render properties."""
        return await make_request("GET", f"{self.url}/replay/render")

    async def post_render_properties(self, options: dict[str, Any]) -> dict[str, Any]:
        """Update render properties."""
        return await make_request("POST", f"{self.url}/replay/render", body=options)

    async def load(self, timeout: int, num_retries: int) -> None:
        """Load replay and wait for it to be ready."""
        response_received = False

        while not response_received and num_retries > 0:
            try:
                await self.get_playback_properties()
                await self.get_recording_properties()
                response_received = True
            except Exception as err:
                num_retries -= 1
                print(
                    f"Couldn't connect to replay API, waiting {timeout} seconds "
                    f"then retrying ({num_retries} retries remaining)."
                )
                await sleep_in_seconds(timeout)

        if num_retries <= 0:
            raise CustomError(
                "Failed to launch replay. Please ensure the replay API is enabled "
                "and the client is running, then try again"
            )

        await self.wait_for_assets_to_load()

    async def wait_for_assets_to_load(self) -> None:
        """Wait for replay assets to load (time >= 15 or paused)."""
        while True:
            playback_state = await self.get_playback_properties()
            time = playback_state.get("time", 0)
            paused = playback_state.get("paused", False)

            if time >= 15 or paused:
                break

    async def wait_for_recording_to_finish(self, time: int) -> None:
        """Wait for recording to finish."""
        wait_time = time

        while True:
            await sleep_in_seconds(wait_time)
            recording_state = await self.get_recording_properties()
            recording = recording_state.get("recording", False)
            current_time = recording_state.get("currentTime", 0)
            end_time = recording_state.get("endTime", 0)
            wait_time = end_time - current_time

            if not recording or wait_time <= 0:
                break

    async def get_all_game_data(self) -> GameData:
        """Get all game data."""
        return await make_request("GET", f"{self.url}/liveclientdata/allgamedata")

    async def get_in_game_position_by_summoner_name(self, summoner_name: str) -> int:
        """Get player position index by summoner name (0-9)."""
        data = await self.get_all_game_data()
        all_players = data.get("allPlayers", [])

        order_team = [p for p in all_players if p.get("team") == "ORDER"]
        chaos_team = [p for p in all_players if p.get("team") == "CHAOS"]

        # Check ORDER team
        for i, player in enumerate(order_team):
            if player.get("riotIdGameName") == summoner_name:
                return i

        # Check CHAOS team
        for i, player in enumerate(chaos_team):
            if player.get("riotIdGameName") == summoner_name:
                return i + 5

        raise CustomError("Summoner not found in game")

    async def focus_by_summoner_name(self, target_summoner_name: str) -> None:
        """Focus camera on a summoner by name."""
        from .league_client import LeagueClient

        position = await self.get_in_game_position_by_summoner_name(target_summoner_name)

        # Map position to keyboard key
        keys = [
            Key.Num1, Key.Num2, Key.Num3, Key.Num4, Key.Num5,
            Key.Q, Key.W, Key.E, Key.R, Key.T,
        ]
        keyboard_key = keys[position]

        execution = LeagueClient()
        handler = WindowHandler()

        for i in range(10):
            await execution.focus_client_window()

            # Press key 50 times
            for j in range(50):
                await handler.keyboard_type(keyboard_key)
                await sleep_in_seconds(0.2)

            await sleep_in_seconds(10)

            # Verify selection
            render_props = await self.get_render_properties()
            selection_name = render_props.get("selectionName", "")

            if selection_name == target_summoner_name:
                break
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/unit/controllers/test_league_replay_client.py -v`
Expected: ALL PASS

**Step 5: Update controllers __init__.py**

Modify: `src/lol_replay_recorder/controllers/__init__.py`

```python
from .window_handler import WindowHandler, Key, Region
from .league_replay_client import LeagueReplayClient

__all__ = ["WindowHandler", "Key", "Region", "LeagueReplayClient"]
```

**Step 6: Commit**

```bash
git add src/lol_replay_recorder/controllers/league_replay_client.py tests/unit/controllers/test_league_replay_client.py src/lol_replay_recorder/controllers/__init__.py
git commit -m "feat: add LeagueReplayClient for replay API control"
```

---

**Note:** This plan continues with additional tasks for:
- Task 14: LeagueClientUx
- Task 15: RiotGameClient
- Task 16: LeagueClient (main orchestrator)
- Task 17-20: Integration tests
- Task 21-22: Documentation and PyPI preparation

Due to length constraints, the remaining tasks follow the same TDD pattern with:
1. Write failing test
2. Run to verify failure
3. Implement minimal code
4. Run to verify pass
5. Commit

Each controller maps its TypeScript counterpart's methods to Python async methods using the established patterns (httpx for HTTP, asyncio for async, pyautogui for automation).
