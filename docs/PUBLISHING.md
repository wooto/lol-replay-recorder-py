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
