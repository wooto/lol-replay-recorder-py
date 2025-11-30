# PyPI 배포 설계

## 개요

lol-replay-recorder를 PyPI 공개 패키지로 배포하기 위한 설계 문서입니다. main 브랜치에 PR이 머지될 때마다 자동으로 patch 버전을 증가시키고 PyPI에 배포합니다.

## 목표

- PyPI에 공개 패키지로 배포
- PR 머지 시 자동으로 버전 업데이트 및 배포
- 매 머지마다 patch 버전 자동 증가 (0.1.0 → 0.1.1 → 0.1.2...)
- 기존 CI 체크(pytest, mypy, ruff) 통과 시에만 배포
- README에 기본 사용 예제 추가

## 배포 파이프라인

### 전체 플로우

1. **PR 머지 감지**: GitHub Actions가 main 브랜치로의 push를 감지
2. **버전 자동 증가**: 현재 버전을 읽어서 patch 버전 증가
3. **품질 검증**: 기존 CI 체크(pytest, mypy, ruff) 통과 확인
4. **패키지 빌드**: `hatchling`으로 wheel과 sdist 빌드
5. **PyPI 배포**: PyPI API 토큰을 사용해 자동 업로드
6. **Git 태그 생성**: 새 버전을 git 태그로 기록 (v0.1.1)

### 장점
- 간단하고 예측 가능
- 모든 머지가 릴리스 가능한 상태여야 한다는 규율 강제
- 수동 개입 최소화

### 단점
- 문서나 내부 리팩토링만 하는 경우에도 새 버전 생성
- 롤백 시 버전 번호 낭비 (PyPI는 같은 버전 재업로드 불가)

## GitHub Actions 워크플로우

### 파일 구조

`.github/workflows/publish.yml` - 새로운 배포 전용 워크플로우

### 워크플로우 구성

**Job 1: 품질 검증 (test)**
- 기존 CI와 동일: pytest, mypy, ruff 실행
- 실패 시 배포 job 실행 안 됨

**Job 2: 버전 업데이트 및 배포 (publish)**
- `needs: test` - test job 성공 후에만 실행
- 단계:
  1. Python 환경 설정
  2. `pyproject.toml`에서 현재 버전 읽기
  3. patch 버전 증가 (예: 0.1.0 → 0.1.1)
  4. `pyproject.toml` 업데이트
  5. 변경사항 커밋 & 푸시
  6. Git 태그 생성 (v0.1.1)
  7. 패키지 빌드 (`python -m build`)
  8. PyPI에 업로드 (`twine` 사용)

### 인증

- PyPI API 토큰을 GitHub Secrets에 `PYPI_API_TOKEN`으로 저장
- 워크플로우에서 `secrets.PYPI_API_TOKEN` 사용

## README 업데이트

### 현재 문제점
- Poetry 언급 (실제로는 uv 사용)
- 사용 예제 없음
- 개발 명령어가 CLAUDE.md와 불일치

### 업데이트 내용

**1. 설치 섹션**
- 최소 Python 버전 요구사항 (>=3.10) 명시
- 지원 OS 명시 (Windows/macOS/Linux)

**2. 기본 사용 예제 추가**
```python
from lol_replay_recorder import LeagueReplayClient

# Replay 클라이언트 초기화 및 로드
client = LeagueReplayClient()
await client.init()
await client.load()

# Replay 제어
await client.play()
await client.pause()
```

**3. 개발 섹션 수정**
- Poetry → uv로 변경
- CLAUDE.md의 명령어와 일치시키기

**4. 선택사항**
- 배지 추가 (PyPI 버전, 라이선스, CI 상태)
- 간단한 기능 설명 (LCU API, Replay API, 윈도우 자동화)

### 원칙
- 너무 길지 않게 유지
- 사용자가 5분 안에 설치해서 첫 replay 녹화 가능한 정도의 정보만 제공

## 패키지 메타데이터 보완

### pyproject.toml에 추가할 항목

**1. 프로젝트 URL들**
```toml
[project.urls]
Homepage = "https://github.com/wooto/lol-replay-recorder-py"
Issues = "https://github.com/wooto/lol-replay-recorder-py/issues"
Source = "https://github.com/wooto/lol-replay-recorder-py"
```

**2. 분류자(Classifiers)**
```toml
classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Operating System :: Microsoft :: Windows",
]
```

**3. Keywords**
```toml
keywords = ["league of legends", "replay", "recording", "lol", "riot games"]
```

**4. Long Description**
- 현재 `readme = "README.md"`로 설정되어 README가 자동으로 PyPI 페이지 설명이 됨
- 명시적으로 content-type 지정 필요

### 목적
- PyPI 페이지를 더 전문적으로 보이게 함
- 검색 가시성 향상
- 사용자가 패키지를 평가하는 데 도움

## 배포 전 준비사항

### 1. PyPI 계정 및 토큰 생성
1. PyPI 계정 생성 (pypi.org)
2. API 토큰 생성 (Account Settings → API tokens)
   - Scope: Entire account 또는 특정 프로젝트
3. GitHub 레포지토리 Settings → Secrets and variables → Actions
4. `PYPI_API_TOKEN` 시크릿 추가

### 2. 패키지 이름 확인
- `lol-replay-recorder`가 PyPI에서 사용 가능한지 확인
- 이미 사용 중이면 대안 고려:
  - `lol-replay-recorder-py`
  - `league-replay-recorder`
  - 기타

### 3. 첫 배포 전략

**옵션 A (권장)**: 수동 첫 배포
1. 메타데이터 및 README 업데이트
2. 로컬에서 빌드 및 테스트
3. 수동으로 0.1.0 배포
4. PyPI 페이지 확인
5. 문제 없으면 자동화 활성화

**옵션 B**: 자동화부터 설정
1. 모든 설정 완료
2. 첫 PR 머지로 0.1.1 자동 배포
3. 리스크 높지만 빠름

### 4. 롤백 계획
- PyPI는 같은 버전 번호 재업로드 불가
- 문제 발생 시:
  - 새 patch 버전으로 수정 배포
  - 급한 경우 PyPI에서 릴리스 yank 처리 (삭제는 불가)
- 자동화 비활성화: 워크플로우 파일 삭제 또는 비활성화

## 구현 순서 (권장)

1. 패키지 메타데이터 보완 (`pyproject.toml`)
2. README 업데이트
3. 패키지 이름 확인 및 PyPI 계정 설정
4. 로컬에서 빌드 테스트
5. 수동으로 0.1.0 배포 및 검증
6. GitHub Actions 워크플로우 작성
7. 자동화 테스트 (별도 브랜치에서)
8. main에 머지하여 자동화 활성화

## 참고사항

### 버전 관리 정책
- Patch 버전만 자동 증가
- Minor/Major 업데이트는 수동으로 `pyproject.toml` 수정 필요
- 예: 0.2.0으로 올리고 싶으면 PR에서 직접 수정

### 모니터링
- GitHub Actions 로그로 배포 상태 확인
- PyPI 페이지에서 다운로드 통계 확인
- 문제 발생 시 GitHub Issues로 피드백 받기

### 향후 개선 가능 사항
- TestPyPI에 먼저 배포 후 검증
- Conventional commits 기반 버전 타입 자동 결정
- 릴리스 노트 자동 생성
- 다운로드 수, 사용 통계 모니터링
