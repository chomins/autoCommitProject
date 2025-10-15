# 설치 가이드

## 빠른 설치 (3분 완료)

### 1️⃣ 전역 설치

```bash
# 저장소 클론
git clone https://github.com/yourusername/autoCommitProject.git
cd autoCommitProject

# 전역 설치
pip install -e .
```

### 2️⃣ 설정 디렉토리 생성

**Windows:**
```cmd
mkdir %USERPROFILE%\.auto-commit
copy config.yaml %USERPROFILE%\.auto-commit\
copy gemini_example.env %USERPROFILE%\.auto-commit\.env
```

**macOS/Linux:**
```bash
mkdir -p ~/.auto-commit
cp config.yaml ~/.auto-commit/
cp gemini_example.env ~/.auto-commit/.env
nano ~/.auto-commit/.env
```

### 3️⃣ API 키 설정

**Gemini (무료, 추천!):**
1. https://aistudio.google.com/app/apikey 접속
2. "Create API Key" 클릭
3. 생성된 키 복사
4. `.env` 파일에 입력:

```env
AI_PROVIDER=gemini
GOOGLE_API_KEY=여기에_발급받은_키_입력
AI_MODEL=gemini-2.0-flash
```

### 4️⃣ 완료!

어떤 프로젝트에서든 사용:

```bash
cd ~/my-project
auto-commit
```

---

## 제거 방법

```bash
# 패키지 제거
pip uninstall auto-commit-ai

# 설정 파일 삭제 (선택사항)
rm -rf ~/.auto-commit  # macOS/Linux
rmdir /s %USERPROFILE%\.auto-commit  # Windows
```

---

## 문제 해결

### pip install 실패
```bash
# Python 버전 확인 (3.7+ 필요)
python --version

# pip 업그레이드
pip install --upgrade pip
```

### 권한 오류 (Windows)
PowerShell을 관리자 권한으로 실행

### 권한 오류 (macOS/Linux)
```bash
sudo pip install -e .
```

---

자세한 사용법은 [README.md](README.md)를 참고하세요.

