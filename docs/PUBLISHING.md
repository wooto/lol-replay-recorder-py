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

## 자동 배포 (Release-Please)

이 프로젝트는 [Release-Please](https://github.com/googleapis/release-please)를 사용하여 버전 관리 및 배포를 자동화합니다.

### 워크플로우

1. **Conventional Commits으로 커밋**
   ```bash
   git commit -m "feat: add new camera control feature"
   git commit -m "fix: resolve replay loading timeout"
   git commit -m "docs: update installation guide"
   ```

2. **main 브랜치에 PR 머지**
   - 일반적인 PR 프로세스 진행

3. **Release-Please가 자동으로 Release PR 생성**
   - PR 제목: "chore(main): release X.Y.Z"
   - 변경사항:
     - `pyproject.toml` 버전 업데이트
     - `src/lol_replay_recorder/__init__.py` 버전 업데이트
     - `CHANGELOG.md` 자동 생성/업데이트

4. **Release PR 검토 및 머지**
   - Release PR을 검토하고 머지
   - 이 단계에서 릴리즈 시점을 제어 가능

5. **자동 배포**
   - GitHub Release 자동 생성
   - Git 태그 생성 (v0.1.1)
   - CI 테스트 실행
   - PyPI에 자동 업로드

### 버전 관리

Release-Please는 Conventional Commits을 분석하여 자동으로 버전을 결정합니다:

- `fix:` → Patch 버전 증가 (0.1.0 → 0.1.1)
- `feat:` → Minor 버전 증가 (0.1.0 → 0.2.0)
- `feat!:` 또는 `BREAKING CHANGE:` → Major 버전 증가 (0.1.0 → 1.0.0)

#### Conventional Commit 타입

- `feat:` - 새 기능
- `fix:` - 버그 수정
- `docs:` - 문서 변경
- `style:` - 코드 포맷팅 (버전 변경 없음)
- `refactor:` - 리팩토링
- `test:` - 테스트 추가/수정
- `chore:` - 빌드/도구 변경 (버전 변경 없음)

#### 수동 버전 지정

특정 버전으로 설정하려면 Release PR의 제목을 수정하면 됩니다.

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
