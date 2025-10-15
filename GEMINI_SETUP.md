# Google Gemini 무료 사용 가이드 🌟

Google Gemini는 **무료 할당량**이 넉넉하고 성능이 뛰어난 AI 모델입니다!  
개인 프로젝트와 소규모 팀에 완벽합니다.

## 왜 Gemini를 사용하나요?

### 💰 가격 비교

| Provider | 무료 할당량 | 가격 (이후) |
|----------|------------|------------|
| **Gemini 2.0 Flash** | ✅ **15 RPM 무료** | 입력: $0.075/1M tokens<br>출력: $0.30/1M tokens |
| **Gemini 1.5 Flash** | ✅ **15 RPM 무료** | 입력: $0.075/1M tokens<br>출력: $0.30/1M tokens |
| OpenAI GPT-4 | ❌ 없음 | 입력: $30/1M tokens<br>출력: $60/1M tokens |
| OpenAI GPT-3.5 | ❌ 없음 | 입력: $0.50/1M tokens<br>출력: $1.50/1M tokens |
| Claude Sonnet | ❌ 없음 | 입력: $3/1M tokens<br>출력: $15/1M tokens |

**Gemini가 가장 경제적입니다!** 특히 개인 프로젝트나 소규모 팀에게 완벽합니다.

## 🚀 빠른 설정

### 1. Google AI Studio에서 API 키 발급

1. **Google AI Studio 접속**
   ```
   https://aistudio.google.com/app/apikey
   ```

2. **Google 계정으로 로그인**

3. **"Create API Key" 클릭**
   - "Create API key in new project" 선택
   - 또는 기존 Google Cloud 프로젝트 선택

4. **API 키 복사**
   - 생성된 키를 안전하게 복사

### 2. .env 파일 설정

```bash
# Windows
notepad %USERPROFILE%\.auto-commit\.env

# macOS/Linux
nano ~/.auto-commit/.env
```

**.env 파일 내용:**
```env
AI_PROVIDER=gemini
GOOGLE_API_KEY=AIzaSyAU6gGGRERt_xBu6jr8t4B2009gnOnBPO8
AI_MODEL=gemini-2.0-flash
```

### 3. 패키지 설치/업데이트

```bash
pip install -r requirements.txt
# 또는
pip install google-generativeai
```

### 4. 테스트

```bash
cd your-project
auto-commit --dry-run
```

완료! 🎉

---

## 📋 사용 가능한 모델

### Gemini 2.0 Flash ⚡ (추천!)
- **모델명:** `gemini-2.0-flash`
- **특징:** 가장 빠르고 효율적
- **최적 용도:** 커밋 메시지 생성에 완벽
- **무료 할당량:** 15 requests/minute

### Gemini 1.5 Pro 🎯
- **모델명:** `gemini-1.5-pro`
- **특징:** 더 정확하고 상세한 분석
- **최적 용도:** 대규모 변경사항이나 복잡한 리팩토링
- **무료 할당량:** 2 requests/minute

### Gemini 1.5 Flash ⚡
- **모델명:** `gemini-1.5-flash`
- **특징:** 빠르고 경제적
- **최적 용도:** 일반적인 커밋
- **무료 할당량:** 15 requests/minute

---

## 🔧 상세 설정

### config.yaml 커스터마이징

```yaml
ai:
  model: "gemini-2.0-flash"  # 또는 gemini-1.5-pro, gemini-1.5-flash
  temperature: 0.3           # 0.0 ~ 1.0 (낮을수록 일관적)
  max_tokens: 500            # 최대 출력 길이
```

### 프로젝트별 다른 모델 사용

**대규모 프로젝트:** (정확도 우선)
```yaml
# big-project/.auto-commit.yaml
ai:
  model: "gemini-1.5-pro"
  temperature: 0.2
```

**소규모 프로젝트:** (속도 우선)
```yaml
# small-project/.auto-commit.yaml
ai:
  model: "gemini-2.0-flash"
  temperature: 0.3
```

---

## 📊 성능 비교

### 테스트: 50줄 변경 커밋 메시지 생성

| 모델 | 응답 시간 | 품질 | 비용 (1000회) |
|------|----------|------|---------------|
| Gemini 2.0 Flash | ~1초 | ⭐⭐⭐⭐ | 무료 |
| Gemini 1.5 Pro | ~2초 | ⭐⭐⭐⭐⭐ | 무료 (제한적) |
| GPT-4 | ~3초 | ⭐⭐⭐⭐⭐ | ~$30 |
| GPT-3.5 | ~1.5초 | ⭐⭐⭐ | ~$2 |

**결론: Gemini 2.0 Flash가 가장 균형잡힌 선택!**

---

## 🌍 실제 사용 예제

### Java Spring Boot 프로젝트

```bash
cd ~/projects/spring-boot-app
# UserService.java, UserController.java 수정
auto-commit
```

**Gemini 생성 메시지:**
```
feat: Add user registration endpoint

- Implement user registration logic in UserService
- Add POST /api/users endpoint in UserController
- Add email validation and password encryption with BCrypt
- Add input validation for user registration
```

### Python Django 프로젝트

```bash
cd ~/projects/django-blog
# models.py, views.py 수정
auto-commit
```

**Gemini 생성 메시지:**
```
fix: Resolve N+1 query issue in post list view

- Add select_related for author in PostListView
- Optimize query to reduce database calls from 100+ to 1
- Add pagination with 20 posts per page
```

### React TypeScript 프로젝트

```bash
cd ~/projects/react-app
# components/*.tsx 수정
auto-commit
```

**Gemini 생성 메시지:**
```
refactor: Convert class components to hooks

- Migrate UserProfile from class to functional component
- Replace componentDidMount with useEffect hook
- Use useState for state management
- Improve code readability and reduce bundle size
```

---

## 💡 팁과 트릭

### 1. 무료 할당량 최적화

```yaml
# 하루에 커밋을 많이 하는 경우
ai:
  model: "gemini-2.0-flash"  # 15 RPM
  temperature: 0.3
```

### 2. 품질 우선 모드

```yaml
# 중요한 릴리스나 대규모 리팩토링
ai:
  model: "gemini-1.5-pro"
  temperature: 0.2
  max_tokens: 800
```

### 3. 빠른 커밋 모드

```yaml
# 작은 변경사항 빠르게 커밋
ai:
  model: "gemini-2.0-flash"
  temperature: 0.5
  max_tokens: 300
```

---

## 🔒 보안 주의사항

### API 키 보호

```bash
# .env 파일 권한 설정 (Unix/Linux)
chmod 600 ~/.auto-commit/.env

# Git에 절대 커밋하지 마세요!
echo ".env" >> .gitignore
```

### API 키 갱신

정기적으로 API 키를 갱신하세요:
1. Google AI Studio에서 기존 키 삭제
2. 새 키 생성
3. .env 파일 업데이트

---

## 🆚 Provider 비교 및 선택 가이드

### Gemini를 선택해야 하는 경우 ✅

- ✅ 무료로 시작하고 싶을 때
- ✅ 개인 프로젝트나 소규모 팀
- ✅ 하루에 여러 번 커밋하는 경우
- ✅ 비용을 절감하고 싶을 때
- ✅ 한국어 지원이 필요할 때 (Gemini는 한국어 우수)

### OpenAI를 선택해야 하는 경우

- 💰 예산이 충분한 경우
- 🎯 최고 품질의 커밋 메시지가 필요할 때
- 🏢 엔터프라이즈 프로젝트

### Anthropic을 선택해야 하는 경우

- 📖 긴 커밋 메시지가 필요할 때 (context window가 큼)
- 🔍 상세한 분석이 필요할 때

---

## 🐛 문제 해결

### "API key not valid" 오류

```bash
# .env 파일 확인
cat ~/.auto-commit/.env

# API 키가 올바른지 Google AI Studio에서 확인
# https://aistudio.google.com/app/apikey
```

### "Quota exceeded" 오류

무료 할당량을 초과한 경우:

**해결 방법 1:** 잠시 기다리기 (1분 후 재시도)

**해결 방법 2:** 더 느린 모델 사용
```env
AI_MODEL=gemini-1.5-pro  # 2 RPM
```

**해결 방법 3:** Google Cloud에서 청구 활성화
- 무료 할당량 이후 유료 사용 가능
- 그래도 매우 저렴함

### "Module not found: google.generativeai"

```bash
pip install google-generativeai
```

---

## 📈 할당량 모니터링

Google AI Studio에서 사용량 확인:
```
https://aistudio.google.com/app/apikey
→ "View usage" 클릭
```

---

## 🎯 권장 설정

### 일반 개발자 (추천)

```env
AI_PROVIDER=gemini
GOOGLE_API_KEY=your-key-here
AI_MODEL=gemini-2.0-flash
```

```yaml
ai:
  model: "gemini-2.0-flash"
  temperature: 0.3
  max_tokens: 500
```

### 품질 중시

```env
AI_PROVIDER=gemini
GOOGLE_API_KEY=your-key-here
AI_MODEL=gemini-1.5-pro
```

```yaml
ai:
  model: "gemini-1.5-pro"
  temperature: 0.2
  max_tokens: 800
```

---

## 🔗 유용한 링크

- [Google AI Studio](https://aistudio.google.com/)
- [Gemini API 문서](https://ai.google.dev/docs)
- [가격 정보](https://ai.google.dev/pricing)
- [Python SDK](https://github.com/google/generative-ai-python)

---

## ✨ 결론

**Gemini는 Auto Commit에 완벽한 선택입니다!**

- ✅ 무료로 시작
- ✅ 훌륭한 성능
- ✅ 빠른 응답
- ✅ 한국어 지원 우수
- ✅ 개인/팀 프로젝트에 이상적

지금 바로 Gemini로 시작하세요! 🚀

