# League of Legends Replay Recorder - Python Port Design

## Overview

TypeScript로 작성된 `@wooto/lol-replay-recorder` 라이브러리를 Python으로 완전 포팅하여 PyPI에 배포 가능한 독립적인 패키지를 만든다.

## 목표

- PyPI 배포 가능한 독립적인 Python 패키지
- TypeScript 원본과 동일한 기능 제공
- Windows 전용 지원 유지
- 현대적인 Python 개발 도구 활용 (uv, Poetry, pytest)

## 프로젝트 구조

```
lol-replay-recorder-py/
├── pyproject.toml              # uv + Poetry 설정
├── README.md
├── src/
│   └── lol_replay_recorder/   # 패키지 루트
│       ├── __init__.py         # 주요 클래스들 export
│       ├── controllers/        # TypeScript의 controller/
│       │   ├── __init__.py
│       │   ├── league_client.py
│       │   ├── league_client_ux.py
│       │   ├── league_replay_client.py
│       │   ├── riot_game_client.py
│       │   └── window_handler.py
│       ├── models/             # TypeScript의 model/
│       │   ├── __init__.py
│       │   ├── custom_error.py
│       │   ├── locale.py
│       │   ├── replay_type.py
│       │   └── riot_types.py
│       ├── apis/               # 설정 파일 편집기
│       │   ├── __init__.py
│       │   ├── ini_editor.py
│       │   └── yaml_editor.py
│       └── utils/
│           ├── __init__.py
│           └── utils.py
├── tests/
│   ├── unit/
│   │   └── apis/
│   │       └── test_ini_editor.py
│   └── e2e/
│       └── lcu/
│           ├── test_league_client.py
│           └── test_riot_game_client.py
└── docs/
    └── plans/
```

### 주요 설계 원칙

- TypeScript의 클래스 기반 구조를 그대로 Python 클래스로 변환
- 네이밍은 snake_case로 (Python 컨벤션)
- 비동기 코드는 `asyncio` 사용 (TypeScript의 async/await과 1:1 매핑)
- 타입 힌팅 적극 활용 (`typing` 모듈, Python 3.10+ 문법)

## 핵심 의존성 매핑

### HTTP/API 클라이언트
- `@fightmegg/riot-api` → `httpx` (비동기 지원)
- `league-connect` → 직접 구현 (lockfile 파싱, LCU API 연결)

### 설정 파일 편집
- `ini` → `configparser` (Python 표준 라이브러리)
- `js-yaml` → `PyYAML` 또는 `ruamel.yaml`

### 윈도우 자동화
- `@kirillvakalov/nut-tree__nut-js` → `pyautogui` + `pygetwindow` 조합
  - 키보드: `pyautogui.press()`, `pyautogui.typewrite()`
  - 마우스: `pyautogui.click()`, `pyautogui.moveTo()`
  - 윈도우 관리: `pygetwindow.getWindowsWithTitle()`

### 프로세스 관리
- `child_process.exec` → `subprocess.run()` (표준 라이브러리)
- taskkill 명령어는 그대로 `subprocess`로 실행

### 유틸리티
- `lodash` → 필요한 함수만 직접 구현 (Python의 list comprehension 등)
- `sleep` → `asyncio.sleep()` / `time.sleep()`

### 개발/테스트 도구
- `mocha` + `chai` → `pytest` + `pytest-asyncio`
- `sinon` → `unittest.mock` 또는 `pytest-mock`
- `typescript` → `mypy` (타입 체킹)

## 윈도우 자동화 레이어 설계

### WindowHandler 구현 전략

```python
# src/lol_replay_recorder/controllers/window_handler.py
from enum import IntEnum
import pyautogui
import pygetwindow as gw
from typing import Optional, List
import asyncio

class Key(IntEnum):
    """TypeScript의 Key enum을 그대로 Python IntEnum으로"""
    Escape = 0
    F1 = 1
    # ... (전체 키 매핑 유지)
    Num1 = 29
    Q = 50
    # ...

class Region:
    """윈도우 영역 정보"""
    def __init__(self, left: int, top: int, width: int, height: int):
        self.left = left
        self.top = top
        self.width = width
        self.height = height
```

### 라이브러리 선택 근거
- `pyautogui`: 키보드/마우스 제어 (크로스 플랫폼이지만 Windows에 최적화)
- `pygetwindow`: Windows 윈도우 관리 (제목으로 찾기, 포커스 등)
- `asyncio`: 비동기 처리 (TypeScript의 async/await 패턴 유지)

### 주의사항
- `nut-tree`의 일부 고급 기능(세밀한 타이밍 제어)은 Python에서 약간 다를 수 있음
- 필요하면 `pywin32`로 더 로우레벨 제어 가능

## API 클라이언트와 비동기 처리

### HTTP 클라이언트

`httpx` 사용 - `requests`와 비슷한 API이지만 async 네이티브 지원:

```python
# src/lol_replay_recorder/models/riot_request.py
import httpx
import ssl
from typing import Any, Dict, Optional

async def make_request(
    method: str,
    url: str,
    headers: Optional[Dict[str, str]] = None,
    data: Optional[Dict[str, Any]] = None
) -> Any:
    """TypeScript의 makeRequest 함수"""
    # TLS 검증 비활성화 (self-signed cert 대응)
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    async with httpx.AsyncClient(verify=False) as client:
        response = await client.request(
            method=method,
            url=url,
            headers=headers,
            json=data
        )
        return response.json()
```

### League Connect 구현

TypeScript의 `league-connect` 라이브러리는 lockfile을 읽어서 LCU 연결하는데, 이를 직접 구현:

```python
# lockfile 파싱 로직
async def read_lockfile(path: str) -> Dict[str, Any]:
    """lockfile에서 포트, 비밀번호 등 추출"""
    # LeagueClient:PID:PORT:PASSWORD:PROTOCOL 형식 파싱
    pass
```

## 타입 시스템과 에러 핸들링

### 타입 힌팅 전략

```python
# src/lol_replay_recorder/models/replay_type.py
from typing import TypedDict, Literal
from dataclasses import dataclass

class RecordingProperties(TypedDict):
    """TypeScript 인터페이스를 TypedDict로"""
    recording: bool
    currentTime: float
    endTime: float

class RenderProperties(TypedDict):
    selectionName: str
    # ...

@dataclass
class GameData:
    """복잡한 타입은 dataclass로"""
    allPlayers: list['Player']
    # ...

# Literal 타입 활용
Team = Literal['ORDER', 'CHAOS']
```

### 커스텀 에러

```python
# src/lol_replay_recorder/models/custom_error.py
class CustomError(Exception):
    """TypeScript의 CustomError 클래스"""
    def __init__(self, message: str, *args):
        super().__init__(message)
        self.args = args
```

### 타입 체킹 도구
- 개발 시 `mypy` 사용 (CI에서 강제)
- Python 3.10+ 문법 활용 (union 타입: `str | None`)

## 테스트 전략

### 테스트 구조

```python
# tests/unit/apis/test_ini_editor.py
import pytest
from lol_replay_recorder.apis.ini_editor import IniEditor

class TestIniEditor:
    """Mocha의 describe 블록을 class로"""

    def test_read_config(self):
        """it('should read config') 스타일"""
        editor = IniEditor("path/to/game.cfg")
        assert editor.data["General"]["EnableReplayApi"] == 1

    @pytest.mark.asyncio
    async def test_async_operation(self):
        """비동기 테스트"""
        # ...
```

### Fixture와 Mocking

```python
# tests/conftest.py
import pytest
from unittest.mock import AsyncMock, patch

@pytest.fixture
def mock_httpx():
    """httpx 모킹"""
    with patch('httpx.AsyncClient') as mock:
        yield mock

@pytest.fixture
def temp_config_file(tmp_path):
    """임시 설정 파일 생성"""
    config_path = tmp_path / "game.cfg"
    # ...
    return config_path
```

### E2E 테스트
- TypeScript처럼 실제 League 클라이언트 필요
- `pytest.mark.e2e` 태그로 분리
- CI에서는 unit만, 로컬에서 e2e 선택적 실행

## 배포 및 패키징 설정

### pyproject.toml

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
    "ruff>=0.1.0",  # linting (eslint 대체)
]

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"

[tool.poetry]
# Poetry 설정
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
```

### 빌드 및 배포 커맨드

```bash
# uv로 의존성 관리
uv pip install -e ".[dev]"

# 빌드
poetry build

# PyPI 배포
poetry publish
```

## 구현 우선순위와 마이그레이션 전략

### Phase 1 - 기본 인프라 (우선순위 높음)
1. 프로젝트 구조 및 `pyproject.toml` 설정
2. 유틸리티 함수 (`utils.py`)
3. 모델/타입 정의 (`models/` 전체)
4. 설정 파일 편집기 (`apis/ini_editor.py`, `apis/yaml_editor.py`)

### Phase 2 - 핵심 컨트롤러 (중요 기능)
5. HTTP 요청 로직 (`riot_request.py`)
6. `LeagueReplayClient` (리플레이 API 연동)
7. `LeagueClientUx` (LCU 연동)
8. `RiotGameClient` (Riot 클라이언트 제어)

### Phase 3 - 자동화 레이어 (복잡함)
9. `WindowHandler` (pyautogui 기반)
10. `LeagueClient` (전체 통합)

### Phase 4 - 테스트 및 문서화
11. Unit 테스트 포팅
12. E2E 테스트 작성
13. README, 사용 예제 작성
14. PyPI 배포 준비

### 마이그레이션 시 주의사항
- 각 Phase 완료 후 간단한 통합 테스트로 검증
- TypeScript 버전과 동작 비교하면서 진행
- Windows 전용 코드는 명확히 문서화
- 비동기 코드 실수 방지 (await 빠뜨리지 않기)

## 다음 단계

디자인 승인 후:
1. git worktree로 격리된 작업 공간 생성
2. 상세 구현 계획 작성 (implementation plan)
3. Phase별로 TDD 방식으로 구현
