# Auto Commit - AI 기반 자동 커밋 도구 🤖

Git 변경사항을 분석하여 자동으로 의미있는 커밋 메시지를 생성하고 커밋하는 도구입니다.

## ✨ 주요 기능

- 📝 Git 변경사항 자동 분석
- 🤖 AI 기반 커밋 메시지 자동 생성
- 💰 **Gemini 무료 할당량** 지원 (추천!)
- 🔧 OpenAI, Anthropic, Google Gemini 지원
- 🌍 **모든 언어** 지원 (Java, Python, JavaScript, Go, C++ 등)
- ✅ 대화형 커밋 확인 및 실행

---

## 🚀 빠른 설치 (전역 설치)

### 1. 저장소 클론 및 설치
```bash
git clone https://github.com/yourusername/autoCommitProject.git
cd autoCommitProject
pip install -e .
```

### 2. 전역 설정 디렉토리 생성
```bash
# Windows
mkdir %USERPROFILE%\.auto-commit
copy config.yaml %USERPROFILE%\.auto-commit\
copy gemini_example.env %USERPROFILE%\.auto-commit\.env

# macOS/Linux
mkdir -p ~/.auto-commit
cp config.yaml ~/.auto-commit/
cp gemini_example.env ~/.auto-commit/.env
```

### 3. API 키 설정

**Gemini 사용 (무료, 추천!):**
```bash
# 1. https://aistudio.google.com/app/apikey 에서 API 키 발급
# 2. .env 파일 편집
notepad %USERPROFILE%\.auto-commit\.env  # Windows
nano ~/.auto-commit/.env                  # macOS/Linux
```

```env
AI_PROVIDER=gemini
GOOGLE_API_KEY=your-google-api-key-here
AI_MODEL=gemini-2.0-flash
```

**또는 OpenAI/Anthropic:**
```env
# OpenAI
AI_PROVIDER=openai
OPENAI_API_KEY=your-openai-key-here

# Anthropic
AI_PROVIDER=anthropic
ANTHROPIC_API_KEY=your-anthropic-key-here
```

### 4. 완료! 🎉

이제 **어떤 프로젝트에서든** 사용 가능합니다:

```bash
# Java 프로젝트
cd ~/projects/spring-boot-app
auto-commit

# Python 프로젝트
cd ~/projects/django-app
auto-commit

# JavaScript 프로젝트
cd ~/projects/react-app
auto-commit

# 짧은 명령어
ac
```

---

## 💡 사용 예제

### 기본 사용
```bash
auto-commit
```

### 주요 옵션
```bash
# 커밋 메시지만 확인 (실제 커밋 안함)
auto-commit --dry-run

# Staged 파일만 커밋
auto-commit --staged-only

# 특정 파일만 커밋
auto-commit --files src/main.py src/utils.py

# 확인 없이 자동 커밋 (CI/CD용)
auto-commit --auto-yes

# 상세 정보 출력
auto-commit --verbose
```

### 실행 예시
```
⚙️  설정 로드 중...
📊 Git 변경사항 분석 중...

┏━━━━━━━━━━━━━━━━┳━━━━━━┓
┃ 항목           ┃ 값   ┃
┡━━━━━━━━━━━━━━━━╇━━━━━━┩
│ Unstaged 파일  │ 3    │
│ 총 파일        │ 3    │
│ 삽입           │ +127 │
│ 삭제           │ -15  │
└────────────────┴──────┘

🤖 AI 커밋 메시지 생성 중...

╭──────────────────────────── 🤖 생성된 커밋 메시지 ────────────────────────────╮
│                                                                               │
│  feat: add user authentication module                                        │
│                                                                               │
╰───────────────────────────────────────────────────────────────────────────────╯

이 메시지로 커밋하시겠습니까? [y/n/e]: y
✅ 커밋 완료! [a3f5b2c]
```

---

## 🌟 왜 Gemini를 추천하나요?

| 특성 | Gemini 2.0 Flash | GPT-4 | GPT-3.5 |
|------|------------------|-------|---------|
| **무료 할당량** | ✅ 15 req/min | ❌ | ❌ |
| **응답 속도** | ~1초 | ~3초 | ~1.5초 |
| **가격** | 무료 → $0.075/1M | $30/1M | $0.50/1M |
| **품질** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |

**Gemini는 무료로 시작할 수 있고 성능도 훌륭합니다!**

자세한 설정: [GEMINI_SETUP.md](GEMINI_SETUP.md)

---

## 🔧 커스터마이징

### 전역 설정
`~/.auto-commit/config.yaml` 편집:

```yaml
ai:
  model: "gemini-2.0-flash"
  temperature: 0.3
  max_tokens: 500

commit:
  conventional_commits: true
  max_subject_length: 72
```

### 프로젝트별 설정
프로젝트 루트에 `.auto-commit.yaml` 생성:

```yaml
ai:
  model: "gemini-1.5-pro"  # 이 프로젝트만 다른 모델 사용
```

---

## 🌍 모든 언어 지원

Auto Commit은 **Git을 사용하는 모든 프로젝트**에서 작동합니다:

✅ Java (Spring Boot, Maven, Gradle)  
✅ Python (Django, Flask, FastAPI)  
✅ JavaScript/TypeScript (React, Vue, Angular, Node.js)  
✅ Go, Rust, C++, C#, Ruby, PHP, Swift, Kotlin  
✅ 그 외 모든 Git 프로젝트

---

## 📚 문서

- **[GEMINI_SETUP.md](GEMINI_SETUP.md)** - Gemini 무료 사용 가이드

---

## 🛠️ 문제 해결

### "API key not valid"
- `.env` 파일의 API 키 확인
- Gemini: https://aistudio.google.com/app/apikey

### "Module not found: google.generativeai"
```bash
pip install -r requirements.txt
```

### "변경사항이 없습니다"
```bash
git status  # 변경사항 확인
git add .   # 파일 staging
```

---

## 📝 커밋 메시지 형식

Conventional Commits 형식을 따릅니다:

- `feat`: 새로운 기능
- `fix`: 버그 수정
- `docs`: 문서 수정
- `refactor`: 코드 리팩토링
- `test`: 테스트 추가/수정
- `chore`: 빌드, 설정 수정
- `perf`: 성능 개선

---

## 🔗 유용한 링크

- **Gemini API 키 발급**: https://aistudio.google.com/app/apikey
- **OpenAI API 키**: https://platform.openai.com/api-keys
- **Anthropic API 키**: https://console.anthropic.com/

---

## 📦 프로젝트 구조

```
autoCommitProject/
├── auto_commit.py              # 메인 실행 파일
├── git_analyzer.py             # Git 변경사항 분석
├── commit_message_generator.py # AI 커밋 메시지 생성
├── config_manager.py           # 설정 관리
├── config.yaml                 # 기본 설정
├── gemini_example.env          # Gemini 설정 예제
├── setup.py                    # 전역 설치 설정
└── requirements.txt            # Python 의존성
```

---

## 📄 라이센스

MIT License - 자유롭게 사용, 수정, 배포 가능합니다.

---

## 🎯 빠른 요약

```bash
# 설치
pip install -e .

# 설정
mkdir ~/.auto-commit
cp config.yaml ~/.auto-commit/
cp gemini_example.env ~/.auto-commit/.env
# API 키 입력

# 사용
cd your-project
auto-commit
```

**끝! 🚀**
