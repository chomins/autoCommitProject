# Auto Commit 설치 가이드 📦

처음 사용하시는 분들을 위한 완전한 설치 가이드입니다.

---

## 📋 목차

1. [사전 준비](#1-사전-준비)
2. [Python 설치](#2-python-설치)
3. [Git 확인](#3-git-확인)
4. [프로젝트 설치](#4-프로젝트-설치)
5. [API 키 발급](#5-api-키-발급)
6. [사용 시작](#6-사용-시작)
7. [문제 해결](#7-문제-해결)

---

## 1. 사전 준비

### 필요한 것들
- ✅ Python 3.7 이상
- ✅ Git
- ✅ 인터넷 연결
- ✅ AI API 키 (Gemini 추천 - 무료!)

---

## 2. Python 설치

### 🪟 Windows

1. **Python 다운로드**
   - https://www.python.org/downloads/ 접속
   - "Download Python 3.x.x" 클릭하여 최신 버전 다운로드

2. **설치**
   - 다운로드한 설치 파일 실행
   - ⚠️ **중요**: "Add Python to PATH" 체크박스 반드시 선택!
   - "Install Now" 클릭

3. **설치 확인**
   ```cmd
   python --version
   pip --version
   ```
   
   버전이 정상적으로 출력되면 성공!

### 🍎 macOS

1. **Homebrew로 설치 (추천)**
   ```bash
   # Homebrew 설치 (없는 경우)
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   
   # Python 설치
   brew install python3
   ```

2. **설치 확인**
   ```bash
   python3 --version
   pip3 --version
   ```

### 🐧 Linux (Ubuntu/Debian)

```bash
# Python 설치
sudo apt update
sudo apt install python3 python3-pip

# 설치 확인
python3 --version
pip3 --version
```

---

## 3. Git 확인

### Git이 설치되어 있는지 확인

```bash
git --version
```

### Git이 없다면 설치

**Windows:**
- https://git-scm.com/download/win 에서 다운로드 후 설치

**macOS:**
```bash
brew install git
```

**Linux:**
```bash
sudo apt install git
```

---

## 4. 프로젝트 설치

### 4-1. 저장소 클론

```bash
# 원하는 위치로 이동 (예: 바탕화면)
cd ~/Desktop

# 또는 Windows
cd %USERPROFILE%\Desktop

# 프로젝트 클론
git clone https://github.com/chomins/autoCommitProject.git

# 프로젝트 디렉토리로 이동
cd autoCommitProject
```

### 4-2. 의존성 패키지 설치

```bash
# 필요한 Python 패키지 설치
pip install -r requirements.txt
```

**또는 Python 3로 명시적으로:**
```bash
pip3 install -r requirements.txt
```

### 4-3. 전역 설치 (어디서든 사용 가능)

```bash
# 개발 모드로 전역 설치
pip install -e .
```

이제 `auto-commit` 또는 `ac` 명령어를 **어떤 디렉토리에서든** 사용할 수 있습니다!

### 4-4. 전역 설정 디렉토리 생성

**🪟 Windows (PowerShell 또는 CMD):**
```cmd
mkdir %USERPROFILE%\.auto-commit
copy config.yaml %USERPROFILE%\.auto-commit\
copy gemini_example.env %USERPROFILE%\.auto-commit\.env
```

**🍎 macOS / 🐧 Linux:**
```bash
mkdir -p ~/.auto-commit
cp config.yaml ~/.auto-commit/
cp gemini_example.env ~/.auto-commit/.env
```

---

## 5. API 키 발급

### 🌟 Gemini 사용 (무료, 추천!)

1. **API 키 발급**
   - https://aistudio.google.com/app/apikey 접속
   - Google 계정으로 로그인
   - "Create API Key" 버튼 클릭
   - 생성된 API 키 복사 (예: `AIzaSyABCDEFG...`)

2. **설정 파일 편집**
   
   **Windows:**
   ```cmd
   notepad %USERPROFILE%\.auto-commit\.env
   ```
   
   **macOS/Linux:**
   ```bash
   nano ~/.auto-commit/.env
   # 또는
   vim ~/.auto-commit/.env
   # 또는
   code ~/.auto-commit/.env
   ```

3. **API 키 입력**
   ```env
   # .env 파일 내용
   AI_PROVIDER=gemini
   GOOGLE_API_KEY=여기에_발급받은_키_붙여넣기
   AI_MODEL=gemini-2.0-flash
   ```
   
   예시:
   ```env
   AI_PROVIDER=gemini
   GOOGLE_API_KEY=AIzaSyABCDEFG1234567890
   AI_MODEL=gemini-2.0-flash
   ```

4. **저장 후 종료**
   - Windows (메모장): `Ctrl + S` 후 닫기
   - nano: `Ctrl + X` → `Y` → `Enter`
   - vim: `ESC` → `:wq` → `Enter`

### 💰 OpenAI 사용 (유료)

1. https://platform.openai.com/api-keys 에서 API 키 발급
2. `.env` 파일에 설정:
   ```env
   AI_PROVIDER=openai
   OPENAI_API_KEY=sk-...
   AI_MODEL=gpt-4o-mini
   ```

### 🤖 Anthropic Claude 사용 (유료)

1. https://console.anthropic.com/ 에서 API 키 발급
2. `.env` 파일에 설정:
   ```env
   AI_PROVIDER=anthropic
   ANTHROPIC_API_KEY=sk-ant-...
   AI_MODEL=claude-3-5-sonnet-20241022
   ```

---

## 6. 사용 시작

### 🎉 설치 완료! 이제 사용해보세요

1. **아무 Git 프로젝트로 이동**
   ```bash
   cd ~/my-project
   ```

2. **파일 수정**
   - 아무 파일이나 수정하거나 새 파일 생성

3. **Auto Commit 실행**
   ```bash
   auto-commit
   ```
   
   또는 짧게:
   ```bash
   ac
   ```

4. **실행 예시**
   ```
   ⚙️  설정 로드 중...
   📊 Git 변경사항 분석 중...
   
   ┏━━━━━━━━━━━━━━━━┳━━━━━━┓
   ┃ 항목           ┃ 값   ┃
   ┡━━━━━━━━━━━━━━━━╇━━━━━━┩
   │ Unstaged 파일  │ 2    │
   │ 총 파일        │ 2    │
   │ 삽입           │ +45  │
   │ 삭제           │ -3   │
   └────────────────┴──────┘
   
   🤖 AI 커밋 메시지 생성 중...
   
   ╭────────── 🤖 생성된 커밋 메시지 ──────────╮
   │                                            │
   │  feat: add user login feature             │
   │                                            │
   ╰────────────────────────────────────────────╯
   
   이 메시지로 커밋하시겠습니까? [y/n/e]: y
   ✅ 커밋 완료! [a3f5b2c]
   ```

### 주요 명령어

```bash
# 기본 사용
auto-commit

# 커밋 메시지만 확인 (실제 커밋 안함)
auto-commit --dry-run

# Staged 파일만 커밋
auto-commit --staged-only

# 특정 파일만 커밋
auto-commit --files file1.py file2.js

# 확인 없이 자동 커밋
auto-commit --auto-yes

# 상세 로그 출력
auto-commit --verbose

# 도움말
auto-commit --help
```

---

## 7. 문제 해결

### ❌ "python: command not found"

**해결책:**
```bash
# Windows: python 대신 py 사용
py --version

# macOS/Linux: python3 사용
python3 --version

# 또는 Python PATH 재설정 필요
```

### ❌ "pip: command not found"

**해결책:**
```bash
# Python과 함께 pip 재설치
python -m ensurepip --upgrade

# 또는
python3 -m pip --version
```

### ❌ "Permission denied" (권한 오류)

**Windows:**
- PowerShell을 **관리자 권한**으로 실행

**macOS/Linux:**
```bash
# 사용자 디렉토리에 설치
pip install --user -e .

# 또는 sudo 사용 (비추천)
sudo pip install -e .
```

### ❌ "auto-commit: command not found"

**원인:** PATH에 Python scripts 경로가 없음

**Windows 해결:**
```cmd
# Python Scripts 경로 확인
where pip

# 출력 예: C:\Users\YourName\AppData\Local\Programs\Python\Python311\Scripts\pip.exe
# 해당 Scripts 폴더를 PATH에 추가
```

**macOS/Linux 해결:**
```bash
# pip install 위치 확인
pip show auto-commit-ai

# .bashrc 또는 .zshrc에 추가
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

### ❌ "API key not valid" 또는 "Invalid API key"

**해결책:**
1. `.env` 파일 경로 확인:
   ```bash
   # Windows
   dir %USERPROFILE%\.auto-commit\.env
   
   # macOS/Linux
   ls -la ~/.auto-commit/.env
   ```

2. `.env` 파일 내용 확인:
   - API 키 앞뒤 공백 제거
   - 따옴표 없이 입력
   - 줄바꿈 없이 입력

3. API 키 재발급:
   - https://aistudio.google.com/app/apikey

### ❌ "No changes detected" (변경사항 없음)

**해결책:**
```bash
# Git 상태 확인
git status

# 파일이 있다면 staging
git add .

# 이제 다시 실행
auto-commit
```

### ❌ "Module not found: google.generativeai"

**해결책:**
```bash
# 의존성 재설치
pip install -r requirements.txt

# 또는 개별 설치
pip install google-generativeai
```

### ❌ 설치는 됐는데 작동 안함

**완전 재설치:**
```bash
# 1. 제거
pip uninstall auto-commit-ai -y

# 2. 캐시 정리
pip cache purge

# 3. 재설치
cd autoCommitProject
pip install -r requirements.txt
pip install -e .

# 4. 확인
auto-commit --help
```

---

## 🗑️ 제거 방법

### 프로그램 제거
```bash
# 패키지 제거
pip uninstall auto-commit-ai

# 설정 파일 삭제 (선택사항)
# Windows
rmdir /s %USERPROFILE%\.auto-commit

# macOS/Linux
rm -rf ~/.auto-commit
```

---

## 🔗 추가 정보

- **상세 사용법**: [README.md](README.md)
- **Gemini 설정**: [GEMINI_SETUP.md](GEMINI_SETUP.md)
- **GitHub 저장소**: https://github.com/chomins/autoCommitProject

---

## 💡 팁

### 설정 커스터마이징

전역 설정 편집:
```bash
# Windows
notepad %USERPROFILE%\.auto-commit\config.yaml

# macOS/Linux
nano ~/.auto-commit/config.yaml
```

프로젝트별 설정 (프로젝트 루트에 생성):
```bash
# .auto-commit.yaml 생성
nano .auto-commit.yaml
```

### 다양한 프로젝트에서 사용

```bash
# Java 프로젝트
cd ~/projects/spring-boot-app
auto-commit

# Python 프로젝트
cd ~/projects/django-app
auto-commit

# JavaScript 프로젝트
cd ~/projects/react-app
ac
```

---

설치 중 문제가 있다면 GitHub Issues에 남겨주세요! 🙋‍♂️

