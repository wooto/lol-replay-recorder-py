# PyPI 배포 구현 계획

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** lol-replay-recorder를 PyPI에 배포하고 PR 머지 시 자동 버전 업데이트 및 배포 설정

**Architecture:** pyproject.toml 메타데이터 보완, README 업데이트, GitHub Actions 워크플로우로 자동 배포 파이프라인 구축

**Tech Stack:** Python packaging (hatchling), GitHub Actions, PyPI, toml 파싱

---

## Task 1: pyproject.toml 메타데이터 보완

**Files:**
- Modify: `pyproject.toml`

**Step 1: 프로젝트 URL 추가**

`pyproject.toml`의 `[project]` 섹션 마지막에 추가:

```toml
[project.urls]
Homepage = "https://github.com/wooto/lol-replay-recorder-py"
Issues = "https://github.com/wooto/lol-replay-recorder-py/issues"
Source = "https://github.com/wooto/lol-replay-recorder-py"
```

**Step 2: Keywords 추가**

`[project]` 섹션의 `license` 라인 다음에 추가:

```toml
keywords = ["league of legends", "replay", "recording", "lol", "riot games"]
```

**Step 3: Classifiers 추가**

`keywords` 라인 다음에 추가:

```toml
classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Operating System :: Microsoft :: Windows",
    "Operating System :: MacOS",
]
```

**Step 4: 변경사항 확인**

Run: `cat pyproject.toml`
Expected: 새로운 메타데이터가 올바르게 추가되었는지 확인

**Step 5: Commit**

```bash
git add pyproject.toml
git commit -m "chore: add PyPI metadata to pyproject.toml"
```

---

## Task 2: README 업데이트

**Files:**
- Modify: `README.md`

**Step 1: 전체 README 재작성**

`README.md`의 전체 내용을 다음으로 교체:

```markdown
# LoL Replay Recorder

A Python library for recording League of Legends replays programmatically.

[![PyPI version](https://badge.fury.io/py/lol-replay-recorder.svg)](https://badge.fury.io/py/lol-replay-recorder)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Features

- **League Client API Integration**: Authenticate with the League Client (LCU API)
- **Replay Control**: Programmatic control of replay playback and recording
- **Window Automation**: Automated camera control and UI interaction during replays

## Requirements

- Python >= 3.10
- League of Legends client installed
- Supported OS: Windows, macOS, Linux

## Installation

```bash
pip install lol-replay-recorder
```

## Quick Start

```python
import asyncio
from lol_replay_recorder import LeagueReplayClient

async def record_replay():
    # Initialize replay client
    client = LeagueReplayClient()
    await client.init()
    await client.load()

    # Control replay playback
    await client.play()
    await asyncio.sleep(5)
    await client.pause()

    # Clean up
    await client.exit()

# Run the async function
asyncio.run(record_replay())
```

## Development

This project uses [uv](https://github.com/astral-sh/uv) for dependency management.

```bash
# Install dependencies
uv sync

# Run tests
uv run pytest

# Run only unit tests
uv run pytest -m unit

# Run type checking
uv run mypy src/

# Run linting
uv run ruff check src/
```

## License

MIT
```

**Step 2: 변경사항 확인**

Run: `cat README.md`
Expected: 새로운 README 내용 확인

**Step 3: Commit**

```bash
git add README.md
git commit -m "docs: update README with installation and usage examples"
```

---

## Task 3: GitHub Actions 배포 워크플로우 작성

**Files:**
- Create: `.github/workflows/publish.yml`

**Step 1: 워크플로우 파일 생성**

`.github/workflows/publish.yml` 파일 생성:

```yaml
name: Publish to PyPI

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v4

    - name: Set up uv
      uses: astral-sh/setup-uv@v3

    - name: Install dependencies
      run: uv sync

    - name: Run tests
      run: uv run pytest

    - name: Run type checking
      run: uv run mypy src/

    - name: Run linting
      run: uv run ruff check src/

  publish:
    needs: test
    runs-on: ubuntu-latest
    permissions:
      contents: write

    steps:
    - uses: actions/checkout@v4
      with:
        fetch-depth: 0
        token: ${{ secrets.GITHUB_TOKEN }}

    - name: Set up uv
      uses: astral-sh/setup-uv@v3

    - name: Configure git
      run: |
        git config user.name "github-actions[bot]"
        git config user.email "github-actions[bot]@users.noreply.github.com"

    - name: Bump version
      id: bump
      run: |
        current_version=$(grep '^version = ' pyproject.toml | sed 's/version = "\(.*\)"/\1/')
        echo "Current version: $current_version"

        IFS='.' read -r major minor patch <<< "$current_version"
        new_patch=$((patch + 1))
        new_version="$major.$minor.$new_patch"
        echo "New version: $new_version"

        sed -i.bak "s/^version = \".*\"/version = \"$new_version\"/" pyproject.toml
        sed -i.bak "s/__version__ = \".*\"/__version__ = \"$new_version\"/" src/lol_replay_recorder/__init__.py
        rm pyproject.toml.bak src/lol_replay_recorder/__init__.py.bak

        echo "version=$new_version" >> $GITHUB_OUTPUT

    - name: Commit version bump
      run: |
        git add pyproject.toml src/lol_replay_recorder/__init__.py
        git commit -m "chore: bump version to ${{ steps.bump.outputs.version }}"
        git push

    - name: Create git tag
      run: |
        git tag "v${{ steps.bump.outputs.version }}"
        git push origin "v${{ steps.bump.outputs.version }}"

    - name: Build package
      run: |
        uv build

    - name: Publish to PyPI
      env:
        TWINE_USERNAME: __token__
        TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
      run: |
        uv run twine upload dist/*
```

**Step 2: twine 의존성 추가**

Run: `uv add --dev twine`
Expected: twine이 dev dependencies에 추가됨

**Step 3: 변경사항 확인**

Run: `cat .github/workflows/publish.yml`
Expected: 워크플로우 파일 내용 확인

**Step 4: Commit**

```bash
git add .github/workflows/publish.yml pyproject.toml
git commit -m "ci: add GitHub Actions workflow for PyPI publishing"
```

---

## Task 4: 로컬 빌드 테스트

**Files:**
- None (테스트만 수행)

**Step 1: 빌드 테스트**

Run: `uv build`
Expected: `dist/` 디렉토리에 `.whl`과 `.tar.gz` 파일 생성

**Step 2: 빌드 결과 확인**

Run: `ls -lh dist/`
Expected:
```
lol_replay_recorder-0.1.0-py3-none-any.whl
lol_replay_recorder-0.1.0.tar.gz
```

**Step 3: dist 디렉토리 정리**

Run: `rm -rf dist/`
Expected: 빌드 산출물 제거 (git에 추가하지 않음)

**Step 4: .gitignore에 dist 추가 확인**

Run: `grep -q "dist/" .gitignore || echo "dist/" >> .gitignore`
Expected: .gitignore에 dist/ 있는지 확인하고 없으면 추가

**Step 5: Commit (if .gitignore changed)**

```bash
git add .gitignore
git commit -m "chore: add dist/ to .gitignore"
```

---

## Task 5: 최종 검증 및 문서화

**Files:**
- Create: `docs/PUBLISHING.md`

**Step 1: 배포 가이드 문서 작성**

`docs/PUBLISHING.md` 파일 생성:

```markdown
# Publishing Guide

## 사전 준비

### 1. PyPI 계정 및 토큰 생성

1. [PyPI](https://pypi.org)에서 계정 생성
2. Account Settings → API tokens에서 새 토큰 생성
   - Token name: `lol-replay-recorder-github-actions`
   - Scope: "Entire account" 또는 프로젝트 생성 후 프로젝트 지정
3. 생성된 토큰 복사 (한 번만 표시됨)

### 2. GitHub Secrets 설정

1. GitHub 레포지토리 → Settings → Secrets and variables → Actions
2. "New repository secret" 클릭
3. Name: `PYPI_API_TOKEN`
4. Value: 복사한 PyPI API 토큰 붙여넣기
5. "Add secret" 클릭

### 3. 패키지 이름 확인

현재 패키지 이름: `lol-replay-recorder`

PyPI에서 이미 사용 중인지 확인:
```bash
pip search lol-replay-recorder
```

만약 이미 사용 중이면 `pyproject.toml`에서 이름 변경 필요.

## 수동 배포 (첫 배포 권장)

```bash
# 1. 빌드
uv build

# 2. TestPyPI에 테스트 업로드 (선택사항)
uv run twine upload --repository testpypi dist/*

# 3. PyPI에 업로드
uv run twine upload dist/*

# 4. 설치 테스트
pip install lol-replay-recorder

# 5. 정리
rm -rf dist/
```

## 자동 배포

main 브랜치에 PR이 머지되면:

1. CI 테스트 실행 (pytest, mypy, ruff)
2. 테스트 통과 시 자동으로 patch 버전 증가 (0.1.0 → 0.1.1)
3. 새 버전을 pyproject.toml과 __init__.py에 커밋
4. Git 태그 생성 (v0.1.1)
5. 패키지 빌드
6. PyPI에 자동 업로드

### 버전 관리

- **Patch 버전**: 자동 증가 (매 PR 머지마다)
- **Minor/Major 버전**: 수동으로 pyproject.toml 수정 후 PR

예: 0.2.0으로 업데이트하려면
```bash
# pyproject.toml에서 version = "0.2.0"으로 수정
# src/lol_replay_recorder/__init__.py에서 __version__ = "0.2.0"으로 수정
git add pyproject.toml src/lol_replay_recorder/__init__.py
git commit -m "chore: bump version to 0.2.0"
```

다음 PR 머지 시 0.2.1로 자동 증가됨.

## 트러블슈팅

### 배포 실패 시

1. GitHub Actions 로그 확인
2. PyPI API 토큰 유효성 확인
3. 패키지 이름 충돌 확인
4. 같은 버전 번호 재업로드 시도하지 않았는지 확인

### 롤백

PyPI는 같은 버전 번호를 재업로드할 수 없으므로:

1. 새 patch 버전으로 수정사항 배포
2. 급한 경우 PyPI에서 문제 버전 "yank" 처리

### 자동화 비활성화

긴급하게 자동 배포를 중단하려면:

```bash
# publish.yml 워크플로우 비활성화
git mv .github/workflows/publish.yml .github/workflows/publish.yml.disabled
git commit -m "ci: temporarily disable auto-publishing"
git push
```

## 모니터링

- GitHub Actions: 배포 상태 확인
- PyPI 페이지: 다운로드 통계, 버전 정보
- GitHub Issues: 사용자 피드백
```

**Step 2: Commit**

```bash
git add docs/PUBLISHING.md
git commit -m "docs: add publishing guide"
```

**Step 3: 모든 테스트 실행**

Run: `uv run pytest`
Expected: 모든 테스트 통과

**Step 4: Type checking 실행**

Run: `uv run mypy src/`
Expected: 타입 체크 통과

**Step 5: Linting 실행**

Run: `uv run ruff check src/`
Expected: Linting 통과

---

## 다음 단계 (수동 작업 필요)

구현 완료 후 Jiho가 직접 수행해야 할 작업:

1. **PyPI 계정 생성 및 토큰 발급**
   - pypi.org에서 계정 생성
   - API 토큰 생성

2. **GitHub Secrets 설정**
   - `PYPI_API_TOKEN` 추가

3. **패키지 이름 확인**
   - `lol-replay-recorder` 사용 가능한지 확인
   - 필요시 이름 변경

4. **첫 배포 테스트** (선택사항이지만 권장)
   - 로컬에서 수동 빌드 및 TestPyPI 배포 테스트
   - 문제 없으면 PyPI에 0.1.0 수동 배포

5. **자동화 활성화**
   - main 브랜치에 머지하여 자동 배포 활성화
   - 첫 자동 배포가 0.1.1이 될 것

---

## 참고사항

### sed 명령어 크로스 플랫폼 이슈

GitHub Actions 워크플로우의 `sed` 명령어는 Linux 환경에서 실행됩니다. macOS의 sed와 문법이 약간 다를 수 있으므로 로컬에서 테스트할 때 주의하세요.

### 버전 자동 증가 로직

워크플로우는 `pyproject.toml`과 `src/lol_replay_recorder/__init__.py` 두 파일의 버전을 동시에 업데이트합니다. 일관성 유지를 위해 두 파일 모두 수동으로 수정할 때도 동기화해야 합니다.
