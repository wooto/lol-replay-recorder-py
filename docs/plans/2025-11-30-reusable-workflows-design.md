# GitHub Actions Reusable Workflows Refactoring

## 목표

GitHub Actions 워크플로우의 중복 코드를 제거하고 재사용 가능한 구조로 리팩토링

## 문제점

기존 `ci.yml`과 `publish.yml`에서 테스트/타입체크/린팅 로직이 중복됨:
- uv 설정 및 의존성 설치
- pytest 실행
- mypy 타입 체크
- ruff 린팅

## 설계

### 파일 구조

```
.github/workflows/
├── test.yml       # Reusable workflow - 테스트/타입체크/린팅
├── ci.yml         # test.yml 호출
└── publish.yml    # test.yml 호출 → PyPI 배포
```

### test.yml (새로 생성)

- `workflow_call` 트리거로 재사용 가능하도록 지정
- 3개 OS matrix에서 테스트 실행 (ubuntu, windows, macos)
- 전체 테스트 실행 (`pytest`)
- 타입 체크 및 린팅 포함

### ci.yml (단순화)

- test.yml을 호출
- 기존 test job의 모든 단계 제거
- aggregation job 추가: "All Tests Passed" status check로 단일 진입점 제공

### publish.yml (단순화)

- test job을 test.yml 호출로 교체
- publish job은 그대로 유지
- 이제 publish 시에도 모든 OS에서 전체 테스트 실행 (기존에는 ubuntu만, unit 테스트만)

## 장점

1. **중복 제거**: 테스트 로직이 한 곳에만 존재
2. **일관성**: CI와 publish가 동일한 테스트 프로세스 사용
3. **유지보수성**: 테스트 단계 수정 시 test.yml만 변경하면 됨
4. **더 강력한 품질 보장**: publish 시에도 모든 OS, 전체 테스트 실행
5. **간단한 branch protection**: "All Tests Passed" 하나만 required status check로 설정

## Required Status Check 처리

Reusable workflow 사용 시 job 이름이 `test / test (os)` 형식으로 변경되는 문제를 aggregation job 패턴으로 해결:

- `status-check` job이 test job의 성공 여부를 확인
- Branch protection에서는 "All Tests Passed" 하나만 required로 설정
- Reusable workflow 내부 변경에 영향받지 않음

**참고:**
- [GitHub Community Discussion #12395](https://github.com/orgs/community/discussions/12395)
- [GitHub Community Discussion #72708](https://github.com/orgs/community/discussions/72708)
