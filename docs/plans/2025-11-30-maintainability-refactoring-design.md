# 유지보수성 향상을 위한 리팩토링 설계

**작성일:** 2025-11-30
**목적:** 전체 프로젝트 구조를 유지보수 관점에서 개선
**접근 방식:** Multi-agent 병렬 분석 기반 통합 설계

---

## 1. 현황 분석

### 1.1 프로젝트 개요

- **총 라인 수:** 2,662 LOC
- **주요 구조:** Controllers (1,668 LOC), Models (747 LOC), APIs (88 LOC), Utils (114 LOC)
- **테스트:** Unit 및 E2E 테스트 분리, pytest 기반

### 1.2 발견된 주요 문제점

4개 관점(아키텍처, 코드 품질, 의존성, 에러 핸들링)에서 분석한 결과:

#### 아키텍처 문제

1. **Models 패키지의 책임 혼재**
   - `models/lcu_request.py`, `models/riot_request.py`에 HTTP 클라이언트 로직 포함
   - 타입 정의와 비즈니스 로직이 혼재
   - 영향: 모듈 임포트 시 불필요한 의존성, 테스트 복잡도 증가

2. **LeagueClient God Object (440 LOC)**
   - 프로세스 관리, 경로 관리, 게임 설정, 윈도우 관리를 한 클래스에서 처리
   - 단일 책임 원칙(SRP) 위반
   - 테스트 어려움, 유지보수 복잡도 높음

3. **APIs 패키지 이름 오해**
   - 실제로는 INI/YAML 파일 편집기인데 `apis/`라는 이름
   - HTTP API와 혼동 가능

#### 코드 품질 문제

1. **HTTP 요청 로직 중복 (80 LOC)**
   - `riot_request.py`와 `lcu_request.py`에 거의 동일한 재시도 로직
   - httpx.AsyncClient 사용 패턴 중복

2. **WindowHandler 중복 인스턴스화**
   - 5개 컨트롤러에서 독립적으로 생성
   - 공유 가능한 리소스를 중복 생성

3. **매직 넘버/스트링 남용**
   - 타임아웃 값 하드코딩 (15초, 60초, 30회, 300회 등)
   - 경로 하드코딩 ("C:\\Riot Games\\...", "/Applications/...")
   - 의미 불명확, 변경 어려움

4. **과도하게 긴 함수/클래스**
   - `LeagueClient`: 440 LOC, 17개 메서드
   - `LeagueClientUx`: 515 LOC, 22개 메서드
   - `start_riot_processes_safely`: 49 LOC

#### 의존성 문제

1. **강한 결합**
   - LeagueClient가 4개 컨트롤러를 직접 인스턴스화
   - 플랫폼별 로직이 클래스 내부에 하드코딩
   - 의존성 주입 없음

2. **인터페이스 추상화 부재**
   - HTTP Client, Config Editor, Window Manager 등에 대한 protocol 없음
   - 테스트 시 mock 주입 어려움

3. **중복 인스턴스 생성**
   - WindowHandler를 각 컨트롤러가 독립적으로 생성
   - 일관성 없는 인스턴스 관리 (lazy vs 즉시 생성)

#### 에러 핸들링 문제

1. **CustomError 사용의 일관성 부족**
   - CustomError 정의되어 있지만 10곳 이상에서 일반 Exception 사용
   - 파일들: riot_request.py, lcu_request.py, league_client.py, ini_editor.py, yaml_editor.py 등

2. **중복된 재시도 로직**
   - riot_request.py와 lcu_request.py에 동일한 재귀 기반 재시도
   - 재시도 횟수가 파일마다 다름 (3, 5, 10회)

3. **불명확한 에러 메시지**
   - "Client Request Error: Max retries exceeded" - URL, 메서드 정보 없음
   - "File not found" - 어떤 파일인지 불명확

4. **에러 무시 패턴 비일관성**
   - 어떤 곳은 조용히 무시 (`except Exception: pass`)
   - 어떤 곳은 print만 하고 무시
   - 기준 불명확, 20곳 이상에서 발견

---

## 2. 목표 아키텍처

### 2.1 레이어 기반 아키텍처

의존성 방향: Controllers → Services → Clients → Domain

```
┌─────────────────────────────────────┐
│ Controllers (Facade Layer)          │
│ - 기존 public API 유지              │
│ - Services 조합으로 기능 제공        │
└─────────────────────────────────────┘
          ↓
┌─────────────────────────────────────┐
│ Services (Business Logic Layer)     │
│ - ProcessManager                     │
│ - ConfigManager                      │
│ - ReplayRecorder                     │
└─────────────────────────────────────┘
          ↓
┌─────────────────────────────────────┐
│ Clients (External Communication)    │
│ - LCUClient                          │
│ - RiotAPIClient                      │
│ - WindowAutomationClient             │
└─────────────────────────────────────┘
          ↓
┌─────────────────────────────────────┐
│ Domain (Pure Types)                 │
│ - Types, Entities, Errors            │
└─────────────────────────────────────┘
```

### 2.2 핵심 원칙

1. **단일 책임 원칙**: 각 모듈은 하나의 명확한 책임
2. **의존성 역전**: 추상화(Protocols)에 의존, 구체 클래스에 직접 의존 금지
3. **개방-폐쇄 원칙**: 확장에는 열려있고 수정에는 닫혀있음
4. **인터페이스 분리**: 필요한 인터페이스만 의존

### 2.3 기대 효과

- **테스트 용이성**: 각 레이어를 독립적으로 테스트 가능
- **변경 영향 최소화**: 레이어 경계로 변경 범위 제한
- **코드 재사용**: 중복 제거로 LOC 30% 감소 예상
- **유지보수성**: 명확한 책임 분리로 버그 수정 시간 단축

---

## 3. 새로운 패키지 구조

### 3.1 디렉토리 구조

```
src/lol_replay_recorder/
├── domain/                    # 296 LOC (타입만)
│   ├── types/
│   │   ├── replay.py         # RecordingProperties, RenderProperties 등
│   │   ├── riot.py           # PlatformId, Region, Cluster
│   │   ├── metadata.py       # PlayerInfo, TeamInfo
│   │   └── locale.py         # Locale enum
│   ├── entities/
│   │   └── summoner.py       # Summoner 엔티티
│   └── errors.py             # CustomError + 확장
│
├── clients/                   # 380 LOC (통합 후)
│   ├── http/
│   │   ├── base.py           # BaseHTTPClient (재시도 로직 통합)
│   │   ├── lcu.py            # LCUClient
│   │   └── riot.py           # RiotAPIClient
│   └── window/
│       └── automation.py     # WindowAutomationClient (기존 WindowHandler)
│
├── services/                  # 950 LOC (새로 생성)
│   ├── process/
│   │   ├── manager.py        # ProcessManager
│   │   └── platform.py       # PlatformResolver (경로, 설정)
│   ├── config/
│   │   ├── editors/
│   │   │   ├── base.py       # ConfigEditor protocol
│   │   │   ├── ini.py        # IniEditor
│   │   │   └── yaml.py       # YamlEditor
│   │   └── game_settings.py  # GameSettingsManager
│   └── replay/
│       └── recorder.py       # ReplayRecorder
│
├── controllers/               # 600 LOC (축소)
│   ├── league_client.py      # LeagueClient (150 LOC로 축소)
│   ├── league_client_ux.py   # LeagueClientUx (300 LOC로 축소)
│   ├── league_replay.py      # LeagueReplayClient
│   └── riot_game.py          # RiotGameClient
│
├── protocols/                 # 80 LOC (새로 생성)
│   ├── http_client.py        # HttpClient protocol
│   ├── config_editor.py      # ConfigEditor protocol
│   └── window_manager.py     # WindowManager protocol
│
└── utils/                     # 114 LOC (유지)
    └── helpers.py
```

### 3.2 주요 변경 사항

#### 이동 및 이름 변경

1. **models/ → domain/**
   - `models/replay_type.py` → `domain/types/replay.py`
   - `models/riot_types.py` → `domain/types/riot.py`
   - `models/metadata_types.py` → `domain/types/metadata.py`
   - `models/locale.py` → `domain/types/locale.py`
   - `models/summoner.py` → `domain/entities/summoner.py`
   - `models/custom_error.py` → `domain/errors.py`

2. **models/ HTTP 클라이언트 분리**
   - `models/riot_request.py` → `clients/http/riot.py` (RiotAPIClient 클래스로)
   - `models/lcu_request.py` → `clients/http/lcu.py` (LCUClient 클래스로)
   - 공통 로직 → `clients/http/base.py` (BaseHTTPClient)

3. **apis/ → services/config/editors/**
   - `apis/ini_editor.py` → `services/config/editors/ini.py`
   - `apis/yaml_editor.py` → `services/config/editors/yaml.py`
   - `protocols/config_editor.py` 추가

4. **controllers/ WindowHandler 이동**
   - `controllers/window_handler.py` → `clients/window/automation.py`

#### 새로 생성

1. **services/process/manager.py**: LeagueClient에서 추출
   - `start_riot_processes_safely()` (64-112줄)
   - `_stop_windows_processes()` (137-174줄)
   - `_stop_unix_processes()` (176-219줄)

2. **services/process/platform.py**: LeagueClient에서 추출
   - `get_installed_paths()` (222-275줄)
   - `get_product_settings_path()` (280-287줄)
   - `get_lockfile_path()` (297-327줄)

3. **services/config/game_settings.py**: LeagueClient에서 추출
   - `set_locale()` (329-360줄)
   - `update_game_config()` (362-398줄)
   - `set_window_mode()` (400-428줄)

4. **clients/http/base.py**: 공통 HTTP 로직
   - 재시도 로직 (riot_request.py와 lcu_request.py에서 통합)
   - SSL 검증 설정
   - 에러 핸들링

5. **protocols/**: 인터페이스 정의
   - `http_client.py`: HttpClient protocol
   - `config_editor.py`: ConfigEditor protocol
   - `window_manager.py`: WindowManager protocol

---

## 4. 단계별 실행 계획

### Phase 1: 기반 작업 (1-2일)

**목표:** 중복 제거, 에러 처리 표준화

#### 1.1 에러 처리 통합

**작업:**
- `domain/errors.py` 생성
  ```python
  class CustomError(Exception):
      """Base error for lol-replay-recorder"""
      pass

  class HTTPError(CustomError):
      """HTTP request failed"""
      def __init__(self, url: str, status_code: int, message: str):
          self.url = url
          self.status_code = status_code
          super().__init__(f"HTTP {status_code} for {url}: {message}")

  class LockfileError(CustomError):
      """Lockfile not found or invalid"""
      pass

  class ProcessError(CustomError):
      """Process management failed"""
      pass

  class ConfigError(CustomError):
      """Configuration error"""
      pass
  ```

- 모든 `Exception` → `CustomError` 변경
  - riot_request.py: 18줄, 45줄
  - lcu_request.py: 71줄, 85줄
  - league_client.py: 92줄
  - ini_editor.py: 26줄, 31줄
  - yaml_editor.py: 18줄, 27줄
  - riot_game_client.py: 214줄

**검증:**
- 모든 unit 테스트 통과
- mypy 타입 체크 통과

#### 1.2 HTTP 클라이언트 통합

**작업:**
- `clients/http/base.py` 생성
  ```python
  class BaseHTTPClient:
      def __init__(self, verify_ssl: bool = False):
          self.client = httpx.AsyncClient(verify=verify_ssl)

      async def request_with_retry(
          self,
          method: str,
          url: str,
          headers: dict[str, str] | None = None,
          body: dict[str, Any] | None = None,
          retries: int = 5,
      ) -> Any:
          """공통 재시도 로직"""
          for attempt in range(retries):
              try:
                  response = await self.client.request(...)
                  if response.is_success:
                      return response.json()
                  if attempt == retries - 1:
                      raise HTTPError(url, response.status_code, ...)
              except httpx.RequestError as e:
                  if attempt == retries - 1:
                      raise HTTPError(url, 0, str(e))
              await asyncio.sleep(0.1 * (attempt + 1))
  ```

- `clients/http/lcu.py` 생성 (LCUClient 클래스)
- `clients/http/riot.py` 생성 (RiotAPIClient 클래스)
- `models/lcu_request.py`, `models/riot_request.py` 제거
- Import 경로 수정 (10+ 파일)

**중복 제거:** 80 LOC

**검증:**
- 모든 HTTP 요청 테스트 통과
- E2E 테스트 통과

#### 1.3 Config Editor 이동

**작업:**
- `services/config/editors/` 디렉토리 생성
- `protocols/config_editor.py` 생성
  ```python
  from typing import Protocol, Any

  class ConfigEditor(Protocol):
      def load(self) -> dict[str, Any]: ...
      def save(self) -> None: ...
      def update(self, path: str, value: Any) -> None: ...
  ```
- `apis/ini_editor.py` → `services/config/editors/ini.py` 이동
- `apis/yaml_editor.py` → `services/config/editors/yaml.py` 이동
- Import 경로 수정 (5개 파일)

**검증:**
- 설정 관련 테스트 통과

---

### Phase 2: 서비스 레이어 구축 (2-3일)

**목표:** 비즈니스 로직 분리, 단일 책임 원칙 적용

#### 2.1 플랫폼 로직 추출

**작업:**
- `services/process/platform.py` 생성
  ```python
  class PlatformResolver:
      """플랫폼별 경로 및 설정 해결"""

      # 상수 정의
      WINDOWS_INSTALL_PATHS = [
          "C:\\Riot Games\\League of Legends",
          "D:\\Riot Games\\League of Legends",
      ]
      MACOS_INSTALL_PATHS = [
          "/Applications/League of Legends.app/Contents/LoL",
      ]

      def get_installed_paths(self) -> list[str]:
          """LeagueClient.get_installed_paths() 이동"""
          pass

      def get_lockfile_path(self) -> str:
          """LeagueClient.get_lockfile_path() 이동"""
          pass

      def get_product_settings_path(self) -> str:
          """LeagueClient.get_product_settings_path() 이동"""
          pass
  ```

- LeagueClient에서 이동:
  - `get_installed_paths()` (222-275줄, 54 LOC)
  - `get_lockfile_path()` (297-327줄, 31 LOC)
  - `get_product_settings_path()` (280-287줄, 8 LOC)

- 하드코딩된 경로를 클래스 상수로 추출

**LOC 절감:** LeagueClient에서 ~100 LOC 제거

**검증:**
- 경로 관련 테스트 통과

#### 2.2 프로세스 관리 분리

**작업:**
- `services/process/manager.py` 생성
  ```python
  class ProcessManager:
      """League 클라이언트 프로세스 관리"""

      def __init__(
          self,
          platform_resolver: PlatformResolver,
          window_client: WindowAutomationClient | None = None
      ):
          self.platform = platform_resolver
          self.window_client = window_client

      async def start_safely(
          self,
          params: dict[str, Any],
          max_attempts: int = 3
      ) -> None:
          """LeagueClient.start_riot_processes_safely() 이동"""
          pass

      async def stop_windows_processes(self) -> None:
          """LeagueClient._stop_windows_processes() 이동"""
          pass

      async def stop_unix_processes(self, pid: int) -> None:
          """LeagueClient._stop_unix_processes() 이동"""
          pass
  ```

- LeagueClient에서 이동:
  - `start_riot_processes_safely()` (64-112줄, 49 LOC)
  - `_stop_windows_processes()` (137-174줄, 38 LOC)
  - `_stop_unix_processes()` (176-219줄, 44 LOC)

- WindowHandler 의존성 주입 패턴 적용

**LOC 절감:** LeagueClient에서 ~130 LOC 제거

**검증:**
- 프로세스 시작/종료 테스트 통과

#### 2.3 게임 설정 서비스

**작업:**
- `services/config/game_settings.py` 생성
  ```python
  class GameSettingsManager:
      """게임 설정 관리"""

      def __init__(
          self,
          platform_resolver: PlatformResolver,
          ini_editor_factory: type[IniEditor] = IniEditor,
          yaml_editor_factory: type[YamlEditor] = YamlEditor,
      ):
          self.platform = platform_resolver
          self.create_ini_editor = ini_editor_factory
          self.create_yaml_editor = yaml_editor_factory

      async def set_locale(self, locale: Locale) -> None:
          """LeagueClient.set_locale() 이동"""
          pass

      async def update_game_config(
          self,
          updates: dict[str, Any]
      ) -> None:
          """LeagueClient.update_game_config() 이동"""
          pass

      async def set_window_mode(
          self,
          enable: bool
      ) -> None:
          """LeagueClient.set_window_mode() 이동"""
          pass
  ```

- LeagueClient에서 이동:
  - `set_locale()` (329-360줄, 32 LOC)
  - `update_game_config()` (362-398줄, 37 LOC)
  - `set_window_mode()` (400-428줄, 29 LOC)

**LOC 절감:** LeagueClient에서 ~100 LOC 제거

**검증:**
- 게임 설정 테스트 통과

---

### Phase 3: 컨트롤러 리팩토링 (2-3일)

**목표:** 컨트롤러를 퍼사드로 축소, 기존 API 유지

#### 3.1 LeagueClient 축소

**작업:**
- LeagueClient를 Services 조합으로 재구성
  ```python
  class LeagueClient:
      """League 클라이언트 메인 퍼사드"""

      def __init__(
          self,
          process_manager: ProcessManager | None = None,
          game_settings_manager: GameSettingsManager | None = None,
          platform_resolver: PlatformResolver | None = None,
          riot_game_client: RiotGameClient | None = None,
          league_client_ux: LeagueClientUx | None = None,
          league_replay_client: LeagueReplayClient | None = None,
      ):
          # 의존성 주입 또는 기본값 생성
          self._platform = platform_resolver or PlatformResolver()
          self._process_manager = process_manager or ProcessManager(self._platform)
          self._game_settings = game_settings_manager or GameSettingsManager(self._platform)

          self.riot_game_client = riot_game_client
          self.league_client_ux = league_client_ux
          self.league_replay_client = league_replay_client

      # Public API는 동일한 시그니처 유지, 내부적으로 services 호출
      async def start_riot_processes_safely(self, params: dict[str, Any]) -> None:
          await self._process_manager.start_safely(params)

      def get_installed_paths(self) -> list[str]:
          return self._platform.get_installed_paths()

      async def set_locale(self, locale: Locale) -> None:
          await self._game_settings.set_locale(locale)

      # ... 나머지 메서드들도 동일 패턴
  ```

**LOC:** 440 LOC → 150 LOC (약 66% 감소)

**검증:**
- 모든 기존 public API 테스트 통과
- 하위 호환성 유지 확인

#### 3.2 기타 컨트롤러 정리

**작업:**
- LeagueClientUx, RiotGameClient도 동일 패턴 적용
- WindowHandler를 싱글톤 또는 의존성 주입으로 공유
  ```python
  # controllers/__init__.py에서 공유 인스턴스 관리
  _window_client = WindowAutomationClient()

  def get_window_client() -> WindowAutomationClient:
      return _window_client
  ```

**검증:**
- 모든 컨트롤러 테스트 통과

#### 3.3 Deprecation 경로 설정

**작업:**
- `models/__init__.py`에 deprecation 경고 추가
  ```python
  import warnings

  # 기존 import 유지 (하위 호환성)
  from ..clients.http.riot import make_request
  from ..clients.http.lcu import make_lcu_request
  from ..domain.errors import CustomError
  from ..domain.types.replay import *
  # ...

  warnings.warn(
      "Importing from 'models' is deprecated. "
      "Use 'domain' for types and 'clients.http' for API calls.",
      DeprecationWarning,
      stacklevel=2
  )
  ```

**검증:**
- 기존 코드가 여전히 작동하는지 확인
- Deprecation 경고가 표시되는지 확인

---

## 5. 마이그레이션 전략

### 5.1 하위 호환성 유지

**원칙:**
- 모든 public API는 동일한 시그니처 유지
- 내부 구현만 변경
- 외부 사용자는 영향 받지 않음

**예시:**
```python
# 외부 사용자 코드 (변경 불필요)
from lol_replay_recorder import LeagueClient

client = LeagueClient()
await client.start_riot_processes_safely(params)

# 내부 구현만 변경됨
# 이전: LeagueClient 내부에서 직접 처리
# 이후: ProcessManager에 위임
```

### 5.2 Deprecation 경로

1. **Phase 1-3 완료 후**: Deprecation 경고 추가
2. **다음 minor 버전 (0.2.0)**: 경고 유지
3. **다음 major 버전 (1.0.0)**: 이전 경로 제거

### 5.3 테스트 전략

**각 Phase 후:**
1. Unit 테스트: `uv run pytest -m unit`
2. E2E 테스트: `uv run pytest -m e2e`
3. 타입 체크: `uv run mypy src/`
4. 린팅: `uv run ruff check src/`

**회귀 방지:**
- 각 Phase 완료 시 커밋
- CI 통과 확인
- 테스트 커버리지 유지 (현재 수준 이상)

### 5.4 롤백 계획

**Git Worktree 사용:**
```bash
# 격리된 브랜치에서 작업
git worktree add ../lol-refactoring -b feature/maintainability-refactoring

# Phase 1 완료
git commit -m "refactor: Phase 1 - foundation work"

# Phase 2 완료
git commit -m "refactor: Phase 2 - service layer"

# Phase 3 완료
git commit -m "refactor: Phase 3 - controller refactoring"
```

**부분 롤백:**
- 각 Phase가 독립적이므로 개별 롤백 가능
- 예: Phase 3에서 문제 발생 시, Phase 2까지만 머지

---

## 6. 검증 및 완료 기준

### 6.1 기능 검증

- [ ] 모든 unit 테스트 통과
- [ ] 모든 E2E 테스트 통과
- [ ] mypy 타입 체크 100% 통과
- [ ] ruff 린팅 0 에러

### 6.2 성능 검증

- [ ] 중복 제거로 LOC 감소 확인 (목표: 30% 감소)
- [ ] HTTP 클라이언트 재사용으로 성능 개선 확인
- [ ] WindowHandler 싱글톤화로 메모리 사용량 감소 확인

### 6.3 유지보수성 검증

- [ ] LeagueClient LOC: 440 → 150 이하
- [ ] 각 서비스 클래스 LOC: 200 이하
- [ ] 순환 의존성 0개
- [ ] 매직 넘버 제거 (모두 상수화)

### 6.4 문서 검증

- [ ] CLAUDE.md 업데이트 (새 구조 반영)
- [ ] README.md 업데이트 (필요 시)
- [ ] API 변경사항 문서화 (CHANGELOG.md)

---

## 7. 예상 일정 및 리소스

### 7.1 일정

- **Phase 1:** 1-2일 (기반 작업)
- **Phase 2:** 2-3일 (서비스 레이어)
- **Phase 3:** 2-3일 (컨트롤러 리팩토링)
- **총 예상:** 5-8일 (테스트 포함)

### 7.2 리스크

1. **E2E 테스트 실패**
   - 완화: Phase별 검증, 즉시 롤백

2. **하위 호환성 깨짐**
   - 완화: Deprecation 경로 유지, 기존 테스트 모두 통과 필수

3. **예상치 못한 의존성**
   - 완화: 작은 단위로 커밋, 자주 테스트

---

## 8. 성공 지표

**정량적 지표:**
- LOC 감소: 2,662 → ~1,850 (30% 감소)
- LeagueClient LOC: 440 → ~150 (66% 감소)
- 중복 코드: 80 LOC 제거
- 테스트 커버리지: 현재 수준 유지 또는 증가

**정성적 지표:**
- 새로운 개발자가 코드베이스 이해 시간 단축
- 버그 수정 시 영향 범위 축소
- 테스트 작성 용이성 향상
- 기능 추가 시 기존 코드 수정 최소화

---

## 9. 다음 단계

1. **설계 문서 리뷰**: Jiho 승인
2. **구현 시작**: Git worktree로 격리된 브랜치 생성
3. **Phase 1 착수**: 에러 처리 통합부터 시작
4. **지속적 검증**: 각 Phase 후 테스트 및 커밋

---

**작성자:** Claude (Bot)
**검토자:** Jiho
**승인 일자:** (검토 후 기입)
