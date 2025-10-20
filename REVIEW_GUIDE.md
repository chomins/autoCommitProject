# 코드 리뷰 기능 가이드

## 🔍 개요

Auto Commit의 코드 리뷰 기능은 **토큰 사용량을 최소화**하면서도 효과적인 코드 리뷰를 제공합니다.

## 💡 핵심 개념

### 토큰 절약 전략

1. **스마트 Diff 압축** (70-80% 토큰 절감)
   - 함수/메서드 시그니처만 추출
   - 주요 로직 변경만 포함 (if, for, return 등)
   - import 문, 공백, 주석 제외
   - 단순 포맷팅 변경 제외

2. **파일 우선순위 필터링**
   - 고우선순위: 핵심 비즈니스 로직, API 엔드포인트
   - 저우선순위: 테스트 파일, 설정 파일 (quick 모드에서 자동 제외)

3. **변경 크기 기반 자동 조절**
   - < 50줄: 상세 리뷰
   - 50-200줄: 중간 리뷰 (핵심만)
   - > 200줄: 간단 리뷰 (요약 + 위험 부분만)

## 📊 리뷰 레벨 상세

### Quick (간단 리뷰)
- **토큰**: ~150 토큰
- **속도**: 매우 빠름
- **용도**: 일상적인 커밋
- **분석**: 
  - ❌ 명백한 버그 (null pointer, logic errors)
  - ⚠️  보안 이슈
  - 🔥 심각한 성능 문제

```bash
auto-commit --review
```

### Normal (일반 리뷰)
- **토큰**: ~400 토큰
- **속도**: 적당함
- **용도**: 중요한 변경사항
- **분석**:
  - ❌ 버그 및 보안
  - ⚠️  잠재적 이슈, 엣지 케이스
  - 💡 코드 품질, 네이밍

```bash
auto-commit --review --review-level normal
```

### Detailed (상세 리뷰)
- **토큰**: ~800 토큰
- **속도**: 느림
- **용도**: 주요 기능 추가, 보안 관련 변경
- **분석**:
  - 🐛 버그 및 로직 오류
  - 🔒 보안 취약점
  - ⚡ 성능 이슈
  - 🏗️  아키텍처 & 디자인 패턴
  - 📝 코드 품질 & 가독성
  - ✨ 베스트 프랙티스

```bash
auto-commit --review-detailed
```

## 🎯 실전 사용 예제

### 시나리오 1: 일상적인 버그 픽스

```bash
# 변경 사항
- src/user_service.py 수정 (30줄)
- 간단한 null check 추가

# 추천 방법
git add src/user_service.py
auto-commit --review

# 결과 (토큰: ~80)
✅ 전반적으로 양호합니다
💡 변수명 개선 제안
```

### 시나리오 2: 새로운 API 엔드포인트 추가

```bash
# 변경 사항
- src/api/payment_controller.py (150줄)
- 결제 처리 로직

# 추천 방법
git add src/api/payment_controller.py
auto-commit --review --review-level normal

# 결과 (토큰: ~350)
⚠️  error handling 개선 필요
💡 트랜잭션 처리 고려 필요
```

### 시나리오 3: 보안 인증 시스템 개선

```bash
# 변경 사항
- src/auth/ (여러 파일, 500줄)
- JWT, OAuth 처리

# 추천 방법
git add src/auth/
auto-commit --review-detailed

# 결과 (토큰: ~700)
🔒 보안: 토큰 만료 시간 검증 추가 필요
⚡ 성능: 캐싱 고려
🏗️  아키텍처: 인증/인가 분리 추천
```

### 시나리오 4: 대량 리팩토링

```bash
# 변경 사항
- 전체 프로젝트 (1000줄 이상)

# 추천 방법 (파일별로 나눠서)
git add src/service1.py
auto-commit --review

git add src/service2.py
auto-commit --review

# 또는 요약 리뷰만
git add .
auto-commit --review-only

# 결과: 대량 변경 자동 감지
⚠️  대량 변경 감지 - 요약 리뷰
📁 .py 파일: 15개 (+500/-200)
  • service1.py (+150/-50)
  • service2.py (+120/-30)
```

## ⚙️ 설정 커스터마이징

### `~/.auto-commit/config.yaml`

```yaml
review:
  # 기본적으로 항상 리뷰 활성화 (NEW!)
  enabled: true                # true면 --review 옵션 없이도 자동 실행
  
  # 기본 리뷰 레벨
  default_level: quick         # quick/normal/detailed
  
  # Temperature (리뷰 정확도)
  temperature: 0.2
  
  # 레벨별 최대 토큰
  max_tokens_quick: 150
  max_tokens_normal: 400
  max_tokens_detailed: 800
  
  # 자동 레벨 조절
  auto_adjust_level: true
  
  # 제외 패턴
  exclude_patterns:
    - "*_test.py"
    - "test_*.py"
    - "*.spec.ts"
    - "*.spec.js"
    - "migrations/*"
    - "*.md"
```

### 기본 동작 설정

**`enabled: true`로 설정하면**:
```bash
# 이렇게만 해도 자동으로 리뷰 실행!
auto-commit

# 리뷰 건너뛰고 싶을 때
auto-commit --no-review
```

**`enabled: false`로 설정하면**:
```bash
# 명시적으로 옵션을 줘야 리뷰 실행
auto-commit --review
```

## 💰 토큰 비용 비교

### Gemini 2.0 Flash (무료 할당량)
- Quick: 무료 (15 req/min 내)
- Normal: 무료
- Detailed: 무료
- **월 예상 비용**: $0 (무료 할당량 내)

### GPT-4 Turbo
- Quick: ~$0.0015 per review
- Normal: ~$0.004 per review
- Detailed: ~$0.008 per review
- **월 예상 비용**: $5-20 (하루 10-20 커밋 기준)

### Claude 3.5 Sonnet
- Quick: ~$0.00045 per review
- Normal: ~$0.0012 per review
- Detailed: ~$0.0024 per review
- **월 예상 비용**: $2-10 (하루 10-20 커밋 기준)

## 🎓 모범 사례

### DO ✅

```bash
# 1. 파일별로 리뷰 (컨텍스트 집중)
git add src/payment.py
auto-commit --review

# 2. 리뷰만 먼저 확인
auto-commit --review-only

# 3. 중요한 파일은 레벨 올리기
auto-commit --review --files src/auth.py --review-level normal

# 4. 일상적 커밋은 quick
git add .
auto-commit --review
```

### DON'T ❌

```bash
# 1. 대량 변경을 detailed로 (비효율)
git add .  # 1000줄 이상
auto-commit --review-detailed  # 토큰 낭비

# 2. 테스트 파일만 detailed로
git add tests/
auto-commit --review-detailed  # 불필요

# 3. 리뷰 없이 중요 변경 커밋
git add src/security.py
auto-commit  # 리뷰 권장!
```

## 🔬 내부 동작 원리

### Diff 압축 과정

1. **파일 우선순위 판단**
   ```python
   high_priority = ["service", "controller", "api", "model"]
   low_priority = ["test_", ".md", "migration"]
   ```

2. **중요 변경사항 추출**
   ```python
   # 포함
   - 함수/클래스 시그니처
   - 로직 변경 (if, for, return)
   - 변수 선언 및 할당
   
   # 제외
   - import 문
   - 공백, 주석
   - 포맷팅 변경
   ```

3. **토큰 추정**
   ```python
   token_estimate = len(compressed_diff) // 4
   # 평균 4자 = 1토큰
   ```

## 📝 출력 형식 예제

### Quick 모드 출력
```
╭──────────── 🔍 AI 코드 리뷰 ────────────╮
│                                        │
│ ✅ 문제 없음                            │
│                                        │
╰────────────────────────────────────────╯
💡 예상 토큰 사용: ~45 tokens
```

### Normal 모드 출력
```
╭──────────── 🔍 AI 코드 리뷰 ────────────╮
│                                        │
│ ✅ 전반적으로 양호합니다                 │
│                                        │
│ ⚠️  주의사항:                          │
│   • user_service.py:45                │
│     null check 누락 가능성              │
│                                        │
│ 💡 제안:                               │
│   • 변수명 개선 권장                    │
│     'tmp' → 'temp_user'               │
│                                        │
╰────────────────────────────────────────╯
💡 예상 토큰 사용: ~120 tokens
```

### Detailed 모드 출력
```
╭──────────── 🔍 AI 코드 리뷰 ────────────╮
│                                        │
│ 🐛 버그:                               │
│   • payment.py:67                     │
│     금액 검증 로직 누락                 │
│                                        │
│ 🔒 보안:                               │
│   • auth.py:23                        │
│     입력값 sanitize 필요               │
│                                        │
│ ⚡ 성능:                                │
│   • service.py:102                    │
│     DB 쿼리 N+1 문제                   │
│                                        │
│ 🏗️  아키텍처:                          │
│   • 비즈니스 로직과 DB 레이어 분리 권장  │
│                                        │
╰────────────────────────────────────────╯
💡 예상 토큰 사용: ~650 tokens
```

## 🚀 고급 기능

### 파일 필터링
```bash
# Python 파일만 리뷰
auto-commit --review --files "*.py"

# 특정 디렉토리만
auto-commit --review --files src/services/

# 여러 파일
auto-commit --review --files auth.py payment.py
```

### 워크플로우 통합
```bash
# 1. 개발
vim src/feature.py

# 2. 리뷰 먼저
auto-commit --review-only

# 3. 수정 반영
vim src/feature.py

# 4. 최종 커밋
auto-commit --review
```

### CI/CD 통합
```yaml
# .github/workflows/review.yml
name: Code Review
on: [pull_request]

jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup Python
        uses: actions/setup-python@v2
      - name: Install Auto Commit
        run: |
          pip install -e .
      - name: Review Changes
        run: |
          auto-commit --review-only --review-level normal
        env:
          AI_PROVIDER: gemini
          GOOGLE_API_KEY: ${{ secrets.GOOGLE_API_KEY }}
```

## 🆘 문제 해결

### "토큰 사용량이 예상보다 많음"
**해결**: 
- `--review-level quick` 사용
- 파일을 나눠서 리뷰
- `config.yaml`에서 `max_tokens_quick` 줄이기

### "리뷰가 너무 간단함"
**해결**:
- `--review-level normal` 또는 `--review-detailed` 사용
- `max_tokens` 늘리기

### "중요한 파일이 제외됨"
**해결**:
- `exclude_patterns` 확인
- 특정 파일 지정: `--files important.py`

## 📚 추가 자료

- [전체 문서](README.md)
- [Gemini 설정 가이드](GEMINI_SETUP.md)
- [GitHub 이슈](https://github.com/chomins/autoCommitProject/issues)

