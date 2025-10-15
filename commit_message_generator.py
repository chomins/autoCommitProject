"""
AI 기반 커밋 메시지 생성기
OpenAI 또는 Anthropic API를 사용하여 커밋 메시지를 생성합니다.
"""

import os
from typing import List, Optional
from abc import ABC, abstractmethod
from git_analyzer import FileChange


class AIProvider(ABC):
    """AI 제공자 추상 클래스"""
    
    @abstractmethod
    def generate_commit_message(self, changes: List[FileChange], config: dict) -> str:
        """커밋 메시지 생성"""
        pass


class OpenAIProvider(AIProvider):
    """OpenAI API 제공자"""
    
    def __init__(self, api_key: str):
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=api_key)
        except ImportError:
            raise ImportError("OpenAI 라이브러리가 설치되지 않았습니다. 'pip install openai'를 실행하세요.")
    
    def generate_commit_message(self, changes: List[FileChange], config: dict) -> str:
        """OpenAI를 사용하여 커밋 메시지 생성"""
        prompt = self._build_prompt(changes, config)
        
        model = config.get('ai', {}).get('model', 'gpt-4')
        temperature = config.get('ai', {}).get('temperature', 0.3)
        max_tokens = config.get('ai', {}).get('max_tokens', 500)
        
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert at writing clear, concise Git commit messages following best practices and Conventional Commits format."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            raise RuntimeError(f"OpenAI API 호출 실패: {e}")
    
    def _build_prompt(self, changes: List[FileChange], config: dict) -> str:
        """프롬프트 생성"""
        use_conventional = config.get('commit', {}).get('conventional_commits', True)
        max_subject_length = config.get('commit', {}).get('max_subject_length', 72)
        
        prompt = "You are a Git commit message expert. Write ONE SPECIFIC commit message.\n\n"
        
        prompt += "🚨 CRITICAL RULES:\n"
        prompt += "1. Be SPECIFIC - say WHAT was added/fixed, not generic terms\n"
        prompt += "2. AVOID: implement, functionality, feature, improve, update, change, endpoint, resource, service, logic\n"
        prompt += "3. USE: add [specific thing], fix [specific bug], refactor [specific part]\n"
        prompt += "4. Max 60 characters, lowercase after colon\n\n"
        
        prompt += "📌 TYPE RULES:\n"
        prompt += "- feat: NEW functionality (new methods/APIs/endpoints)\n"
        prompt += "- fix: BUG fix (fixing broken behavior)\n"
        prompt += "- refactor: Code restructure (NO new features)\n\n"
        
        prompt += "✅ GOOD (SPECIFIC):\n"
        prompt += "- feat: add config comparison validation\n"
        prompt += "- feat: add JWT token refresh endpoint\n"
        prompt += "- feat: add rollback handling for transfers\n"
        prompt += "- fix: null pointer in user lookup\n"
        prompt += "- fix: validation error in email format\n\n"
        
        prompt += "❌ BAD (TOO GENERIC - FORBIDDEN!):\n"
        prompt += "- feat: implement transfer functionality ❌\n"
        prompt += "- feat: add new feature ❌\n"
        prompt += "- feat: improve service ❌\n"
        prompt += "- fix: update code ❌\n"
        prompt += "- refactor: restructure code ❌\n\n"
        
        prompt += "💡 HOW TO BE SPECIFIC:\n"
        prompt += "Look at method names, endpoints, class names in the diff!\n"
        prompt += "- See 'compareConfigs()' → say 'add config comparison'\n"
        prompt += "- See 'validateTransfer()' → say 'add transfer validation'\n"
        prompt += "- See '@POST /rollback' → say 'add rollback endpoint'\n\n"
        
        prompt += "Git Changes:\n"
        prompt += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        
        for change in changes:
            change_symbol = {
                'A': '🆕 ADDED (NEW FILE)',
                'M': '📝 MODIFIED',
                'D': '🗑️  DELETED',
                'R': '📋 RENAMED'
            }.get(change.change_type, 'CHANGED')
            
            prompt += f"\nFile: {change.path} ({change_symbol})\n"
            prompt += f"Stats: +{change.insertions} / -{change.deletions} lines\n"
            
            # Diff 내용을 더 상세히 포함
            if change.diff:
                diff_lines = change.diff.split('\n')
                
                # 모든 변경사항 포함 (제한을 크게 늘림)
                added_lines = []
                removed_lines = []
                new_methods = []
                endpoints = []
                
                for line in diff_lines[:200]:  # 처음 200줄까지 확장
                    if line.startswith('+') and not line.startswith('+++'):
                        added_line = line[1:].strip()
                        added_lines.append(added_line)
                        # 새로운 메서드/함수 감지
                        if any(keyword in added_line for keyword in ['public ', 'private ', 'protected ', 'def ', 'function ', 'async ', '@']):
                            if '(' in added_line:
                                new_methods.append(added_line)
                        # 엔드포인트/매핑 어노테이션 감지
                        if added_line.startswith('@') and any(marker in added_line for marker in ['Mapping', 'RequestMapping', 'Path', 'Route']):
                            endpoints.append(added_line)
                    elif line.startswith('-') and not line.startswith('---'):
                        removed_lines.append(line[1:].strip())
                
                # 🚨 새 메서드가 많으면 반드시 강조
                if new_methods:
                    prompt += f"\n⚠️  DETECTED {len(new_methods)} NEW METHODS/FUNCTIONS - This is likely a FEAT, not refactor!\n"
                    prompt += "New methods:\n"
                    for method in new_methods[:10]:
                        prompt += f"  + {method[:120]}\n"
                # 📌 감지된 엔드포인트/어노테이션 노출
                if endpoints:
                    prompt += "Detected endpoints/annotations:\n"
                    for ep in endpoints[:8]:
                        prompt += f"  + {ep[:120]}\n"
                
                if added_lines or removed_lines:
                    prompt += "\nKey changes:\n"
                    
                    if added_lines:
                        prompt += f"  ADDED ({len(added_lines)} lines):\n"
                        for line in added_lines[:20]:  # 추가된 줄 20개로 확대
                            if line and len(line) > 3:  # 빈 줄 제외
                                prompt += f"    + {line[:120]}\n"
                    
                    if removed_lines:
                        prompt += f"  REMOVED ({len(removed_lines)} lines):\n"
                        for line in removed_lines[:10]:  # 삭제된 줄 10개
                            if line and len(line) > 3:  # 빈 줄 제외
                                prompt += f"    - {line[:100]}\n"
        
        prompt += "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        prompt += "\n🎯 YOUR TASK: Read the ACTUAL method names above and write a commit message.\n\n"
        prompt += "📖 STEP 1: Look at 'DETECTED NEW METHODS/FUNCTIONS' section.\n"
        prompt += "   Extract ACTION from each method name:\n"
        prompt += "   - Method name format: `actionSubject` (e.g., `getUserData`, `validateEmail`, `exportReport`)\n"
        prompt += "   - Extract: action + what (e.g., 'get user data', 'validate email', 'export report')\n\n"
        prompt += "🚨 CRITICAL: Use ONLY what you see in the actual method names. Do NOT invent!\n\n"
        prompt += "📝 STEP 2: Decide commit type.\n"
        prompt += "   - NEW public methods/APIs → `feat:`\n"
        prompt += "   - Code restructure only → `refactor:`\n\n"
        prompt += "✍️ STEP 3: Write message (max 60 chars).\n"
        prompt += "   Format: `feat: add [action1], [action2]`\n"
        prompt += "   Example pattern: `feat: add user retrieval, email validation`\n\n"
        prompt += "❌ FORBIDDEN: endpoint, resource, service, logic, functionality, operations\n"
        prompt += "✅ ALLOWED: list, get, compare, transfer, export, validate, import, delete\n\n"
        prompt += "Write commit message based on ACTUAL method names:"
        
        return prompt


class GeminiProvider(AIProvider):
    """Google Gemini API 제공자"""
    
    def __init__(self, api_key: str):
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            self.genai = genai
        except ImportError:
            raise ImportError("Google Generative AI 라이브러리가 설치되지 않았습니다. 'pip install google-generativeai'를 실행하세요.")
    
    def generate_commit_message(self, changes: List[FileChange], config: dict) -> str:
        """Google Gemini를 사용하여 커밋 메시지 생성"""
        prompt = self._build_prompt(changes, config)
        
        model_name = config.get('ai', {}).get('model', 'gemini-2.0-flash')
        temperature = config.get('ai', {}).get('temperature', 0.2)
        max_tokens = config.get('ai', {}).get('max_tokens', 100)
        
        try:
            model = self.genai.GenerativeModel(model_name)
            
            generation_config = {
                "temperature": temperature,
                "max_output_tokens": max_tokens,
            }
            
            response = model.generate_content(
                prompt,
                generation_config=generation_config
            )
            
            return response.text.strip()
        except Exception as e:
            raise RuntimeError(f"Gemini API 호출 실패: {e}")
    
    def _build_prompt(self, changes: List[FileChange], config: dict) -> str:
        """프롬프트 생성"""
        prompt = "You are a Git commit message expert. Write ONE SPECIFIC commit message.\n\n"
        
        prompt += "🚨 CRITICAL RULES:\n"
        prompt += "1. Be SPECIFIC - say WHAT was added/fixed, not generic terms\n"
        prompt += "2. AVOID: implement, functionality, feature, improve, update, change, endpoint, resource, service, logic\n"
        prompt += "3. USE: add [specific thing], fix [specific bug], refactor [specific part]\n"
        prompt += "4. Max 60 characters, lowercase after colon\n\n"
        
        prompt += "📌 TYPE RULES:\n"
        prompt += "- feat: NEW functionality (new methods/APIs/endpoints)\n"
        prompt += "- fix: BUG fix (fixing broken behavior)\n"
        prompt += "- refactor: Code restructure (NO new features)\n\n"
        
        prompt += "✅ GOOD (SPECIFIC):\n"
        prompt += "- feat: add config comparison validation\n"
        prompt += "- feat: add JWT token refresh endpoint\n"
        prompt += "- feat: add rollback handling for transfers\n"
        prompt += "- fix: null pointer in user lookup\n"
        prompt += "- fix: validation error in email format\n\n"
        
        prompt += "❌ BAD (TOO GENERIC - FORBIDDEN!):\n"
        prompt += "- feat: implement transfer functionality ❌\n"
        prompt += "- feat: add new feature ❌\n"
        prompt += "- feat: improve service ❌\n"
        prompt += "- fix: update code ❌\n"
        prompt += "- refactor: restructure code ❌\n\n"
        
        prompt += "💡 HOW TO BE SPECIFIC:\n"
        prompt += "Look at method names, endpoints, class names in the diff!\n"
        prompt += "- See 'compareConfigs()' → say 'add config comparison'\n"
        prompt += "- See 'validateTransfer()' → say 'add transfer validation'\n"
        prompt += "- See '@POST /rollback' → say 'add rollback endpoint'\n\n"
        
        prompt += "Git Changes:\n"
        prompt += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        
        for change in changes:
            change_symbol = {
                'A': '🆕 ADDED (NEW FILE)',
                'M': '📝 MODIFIED',
                'D': '🗑️  DELETED',
                'R': '📋 RENAMED'
            }.get(change.change_type, 'CHANGED')
            
            prompt += f"\nFile: {change.path} ({change_symbol})\n"
            prompt += f"Stats: +{change.insertions} / -{change.deletions} lines\n"
            
            # Diff 내용을 더 상세히 포함
            if change.diff:
                diff_lines = change.diff.split('\n')
                
                # 모든 변경사항 포함 (제한을 크게 늘림)
                added_lines = []
                removed_lines = []
                new_methods = []
                endpoints = []
                
                for line in diff_lines[:200]:  # 처음 200줄까지 확장
                    if line.startswith('+') and not line.startswith('+++'):
                        added_line = line[1:].strip()
                        added_lines.append(added_line)
                        # 새로운 메서드/함수 감지
                        if any(keyword in added_line for keyword in ['public ', 'private ', 'protected ', 'def ', 'function ', 'async ', '@']):
                            if '(' in added_line:
                                new_methods.append(added_line)
                        # 엔드포인트/매핑 어노테이션 감지
                        if added_line.startswith('@') and any(marker in added_line for marker in ['Mapping', 'RequestMapping', 'Path', 'Route']):
                            endpoints.append(added_line)
                    elif line.startswith('-') and not line.startswith('---'):
                        removed_lines.append(line[1:].strip())
                
                # 🚨 새 메서드가 많으면 반드시 강조
                if new_methods:
                    prompt += f"\n⚠️  DETECTED {len(new_methods)} NEW METHODS/FUNCTIONS - This is likely a FEAT, not refactor!\n"
                    prompt += "New methods:\n"
                    for method in new_methods[:10]:
                        prompt += f"  + {method[:120]}\n"
                # 📌 감지된 엔드포인트/어노테이션 노출
                if endpoints:
                    prompt += "Detected endpoints/annotations:\n"
                    for ep in endpoints[:8]:
                        prompt += f"  + {ep[:120]}\n"
                
                if added_lines or removed_lines:
                    prompt += "\nKey changes:\n"
                    
                    if added_lines:
                        prompt += f"  ADDED ({len(added_lines)} lines):\n"
                        for line in added_lines[:20]:  # 추가된 줄 20개로 확대
                            if line and len(line) > 3:  # 빈 줄 제외
                                prompt += f"    + {line[:120]}\n"
                    
                    if removed_lines:
                        prompt += f"  REMOVED ({len(removed_lines)} lines):\n"
                        for line in removed_lines[:10]:  # 삭제된 줄 10개
                            if line and len(line) > 3:  # 빈 줄 제외
                                prompt += f"    - {line[:100]}\n"
        
        prompt += "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        prompt += "\n🎯 YOUR TASK: Read the ACTUAL method names above and write a commit message.\n\n"
        prompt += "📖 STEP 1: Look at 'DETECTED NEW METHODS/FUNCTIONS' section.\n"
        prompt += "   Extract ACTION from each method name:\n"
        prompt += "   - Method name format: `actionSubject` (e.g., `getUserData`, `validateEmail`, `exportReport`)\n"
        prompt += "   - Extract: action + what (e.g., 'get user data', 'validate email', 'export report')\n\n"
        prompt += "🚨 CRITICAL: Use ONLY what you see in the actual method names. Do NOT invent!\n\n"
        prompt += "📝 STEP 2: Decide commit type.\n"
        prompt += "   - NEW public methods/APIs → `feat:`\n"
        prompt += "   - Code restructure only → `refactor:`\n\n"
        prompt += "✍️ STEP 3: Write message (max 60 chars).\n"
        prompt += "   Format: `feat: add [action1], [action2]`\n"
        prompt += "   Example pattern: `feat: add user retrieval, email validation`\n\n"
        prompt += "❌ FORBIDDEN: endpoint, resource, service, logic, functionality, operations\n"
        prompt += "✅ ALLOWED: list, get, compare, transfer, export, validate, import, delete\n\n"
        prompt += "Write commit message based on ACTUAL method names:"
        
        return prompt


class AnthropicProvider(AIProvider):
    """Anthropic (Claude) API 제공자"""
    
    def __init__(self, api_key: str):
        try:
            import anthropic
            self.client = anthropic.Anthropic(api_key=api_key)
        except ImportError:
            raise ImportError("Anthropic 라이브러리가 설치되지 않았습니다. 'pip install anthropic'을 실행하세요.")
    
    def generate_commit_message(self, changes: List[FileChange], config: dict) -> str:
        """Anthropic Claude를 사용하여 커밋 메시지 생성"""
        prompt = self._build_prompt(changes, config)
        
        model = config.get('ai', {}).get('model', 'claude-3-sonnet-20240229')
        temperature = config.get('ai', {}).get('temperature', 0.3)
        max_tokens = config.get('ai', {}).get('max_tokens', 500)
        
        try:
            response = self.client.messages.create(
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                system="You are an expert at writing clear, concise Git commit messages following best practices and Conventional Commits format.",
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            return response.content[0].text.strip()
        except Exception as e:
            raise RuntimeError(f"Anthropic API 호출 실패: {e}")
    
    def _build_prompt(self, changes: List[FileChange], config: dict) -> str:
        """프롬프트 생성 (OpenAI/Anthropic과 동일)"""
        prompt = "You are a Git commit message expert. Write ONE SPECIFIC commit message.\n\n"
        
        prompt += "🚨 CRITICAL RULES:\n"
        prompt += "1. Be SPECIFIC - say WHAT was added/fixed, not generic terms\n"
        prompt += "2. AVOID: implement, functionality, feature, improve, update, change, endpoint, resource, service, logic\n"
        prompt += "3. USE: add [specific thing], fix [specific bug], refactor [specific part]\n"
        prompt += "4. Max 60 characters, lowercase after colon\n\n"
        
        prompt += "📌 TYPE RULES:\n"
        prompt += "- feat: NEW functionality (new methods/APIs/endpoints)\n"
        prompt += "- fix: BUG fix (fixing broken behavior)\n"
        prompt += "- refactor: Code restructure (NO new features)\n\n"
        
        prompt += "✅ GOOD (SPECIFIC):\n"
        prompt += "- feat: add config comparison validation\n"
        prompt += "- feat: add JWT token refresh endpoint\n"
        prompt += "- feat: add rollback handling for transfers\n"
        prompt += "- fix: null pointer in user lookup\n"
        prompt += "- fix: validation error in email format\n\n"
        
        prompt += "❌ BAD (TOO GENERIC - FORBIDDEN!):\n"
        prompt += "- feat: implement transfer functionality ❌\n"
        prompt += "- feat: add new feature ❌\n"
        prompt += "- feat: improve service ❌\n"
        prompt += "- fix: update code ❌\n"
        prompt += "- refactor: restructure code ❌\n\n"
        
        prompt += "💡 HOW TO BE SPECIFIC:\n"
        prompt += "Look at method names, endpoints, class names in the diff!\n"
        prompt += "- See 'compareConfigs()' → say 'add config comparison'\n"
        prompt += "- See 'validateTransfer()' → say 'add transfer validation'\n"
        prompt += "- See '@POST /rollback' → say 'add rollback endpoint'\n\n"
        
        prompt += "Git Changes:\n"
        prompt += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        
        for change in changes:
            change_symbol = {
                'A': '🆕 ADDED (NEW FILE)',
                'M': '📝 MODIFIED',
                'D': '🗑️  DELETED',
                'R': '📋 RENAMED'
            }.get(change.change_type, 'CHANGED')
            
            prompt += f"\nFile: {change.path} ({change_symbol})\n"
            prompt += f"Stats: +{change.insertions} / -{change.deletions} lines\n"
            
            # Diff 내용을 더 상세히 포함
            if change.diff:
                diff_lines = change.diff.split('\n')
                
                # 모든 변경사항 포함 (제한을 크게 늘림)
                added_lines = []
                removed_lines = []
                new_methods = []
                endpoints = []
                
                for line in diff_lines[:200]:  # 처음 200줄까지 확장
                    if line.startswith('+') and not line.startswith('+++'):
                        added_line = line[1:].strip()
                        added_lines.append(added_line)
                        # 새로운 메서드/함수 감지
                        if any(keyword in added_line for keyword in ['public ', 'private ', 'protected ', 'def ', 'function ', 'async ', '@']):
                            if '(' in added_line:
                                new_methods.append(added_line)
                        # 엔드포인트/매핑 어노테이션 감지
                        if added_line.startswith('@') and any(marker in added_line for marker in ['Mapping', 'RequestMapping', 'Path', 'Route']):
                            endpoints.append(added_line)
                    elif line.startswith('-') and not line.startswith('---'):
                        removed_lines.append(line[1:].strip())
                
                # 🚨 새 메서드가 많으면 반드시 강조
                if new_methods:
                    prompt += f"\n⚠️  DETECTED {len(new_methods)} NEW METHODS/FUNCTIONS - This is likely a FEAT, not refactor!\n"
                    prompt += "New methods:\n"
                    for method in new_methods[:10]:
                        prompt += f"  + {method[:120]}\n"
                # 📌 감지된 엔드포인트/어노테이션 노출
                if endpoints:
                    prompt += "Detected endpoints/annotations:\n"
                    for ep in endpoints[:8]:
                        prompt += f"  + {ep[:120]}\n"
                
                if added_lines or removed_lines:
                    prompt += "\nKey changes:\n"
                    
                    if added_lines:
                        prompt += f"  ADDED ({len(added_lines)} lines):\n"
                        for line in added_lines[:20]:  # 추가된 줄 20개로 확대
                            if line and len(line) > 3:  # 빈 줄 제외
                                prompt += f"    + {line[:120]}\n"
                    
                    if removed_lines:
                        prompt += f"  REMOVED ({len(removed_lines)} lines):\n"
                        for line in removed_lines[:10]:  # 삭제된 줄 10개
                            if line and len(line) > 3:  # 빈 줄 제외
                                prompt += f"    - {line[:100]}\n"
        
        prompt += "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        prompt += "\n🎯 YOUR TASK: Read the ACTUAL method names above and write a commit message.\n\n"
        prompt += "📖 STEP 1: Look at 'DETECTED NEW METHODS/FUNCTIONS' section.\n"
        prompt += "   Extract ACTION from each method name:\n"
        prompt += "   - Method name format: `actionSubject` (e.g., `getUserData`, `validateEmail`, `exportReport`)\n"
        prompt += "   - Extract: action + what (e.g., 'get user data', 'validate email', 'export report')\n\n"
        prompt += "🚨 CRITICAL: Use ONLY what you see in the actual method names. Do NOT invent!\n\n"
        prompt += "📝 STEP 2: Decide commit type.\n"
        prompt += "   - NEW public methods/APIs → `feat:`\n"
        prompt += "   - Code restructure only → `refactor:`\n\n"
        prompt += "✍️ STEP 3: Write message (max 60 chars).\n"
        prompt += "   Format: `feat: add [action1], [action2]`\n"
        prompt += "   Example pattern: `feat: add user retrieval, email validation`\n\n"
        prompt += "❌ FORBIDDEN: endpoint, resource, service, logic, functionality, operations\n"
        prompt += "✅ ALLOWED: list, get, compare, transfer, export, validate, import, delete\n\n"
        prompt += "Write commit message based on ACTUAL method names:"
        
        return prompt


class CommitMessageGenerator:
    """커밋 메시지 생성기 메인 클래스"""
    
    def __init__(self, provider: str = "openai", api_key: Optional[str] = None):
        """
        Args:
            provider: 'openai', 'anthropic', 또는 'gemini'
            api_key: API 키 (None이면 환경 변수에서 가져옴)
        """
        if api_key is None:
            if provider == "openai":
                api_key = os.getenv("OPENAI_API_KEY")
                if not api_key:
                    raise ValueError("OPENAI_API_KEY 환경 변수가 설정되지 않았습니다.")
            elif provider == "anthropic":
                api_key = os.getenv("ANTHROPIC_API_KEY")
                if not api_key:
                    raise ValueError("ANTHROPIC_API_KEY 환경 변수가 설정되지 않았습니다.")
            elif provider == "gemini":
                api_key = os.getenv("GOOGLE_API_KEY")
                if not api_key:
                    raise ValueError("GOOGLE_API_KEY 환경 변수가 설정되지 않았습니다.")
            else:
                raise ValueError(f"지원하지 않는 provider: {provider}")
        
        if provider == "openai":
            self.provider = OpenAIProvider(api_key)
        elif provider == "anthropic":
            self.provider = AnthropicProvider(api_key)
        elif provider == "gemini":
            self.provider = GeminiProvider(api_key)
        else:
            raise ValueError(f"지원하지 않는 provider: {provider}. 'openai', 'anthropic', 또는 'gemini'를 사용하세요.")
    
    def generate(self, changes: List[FileChange], config: dict) -> str:
        """커밋 메시지 생성"""
        if not changes:
            raise ValueError("변경사항이 없습니다.")
        
        return self.provider.generate_commit_message(changes, config)


if __name__ == "__main__":
    # 테스트 코드
    from git_analyzer import GitAnalyzer
    import yaml
    
    # 설정 로드
    with open('config.yaml', 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    # Git 변경사항 분석
    analyzer = GitAnalyzer()
    
    if not analyzer.has_changes():
        print("변경사항이 없습니다.")
        exit(0)
    
    changes = analyzer.get_all_changes(include_untracked=True)
    all_changes = changes.staged_files + changes.unstaged_files
    
    if not all_changes:
        print("변경사항이 없습니다.")
        exit(0)
    
    # AI 제공자 선택
    provider = os.getenv("AI_PROVIDER", "openai")
    
    print(f"🤖 {provider.upper()}를 사용하여 커밋 메시지 생성 중...")
    
    # 커밋 메시지 생성
    generator = CommitMessageGenerator(provider=provider)
    message = generator.generate(all_changes, config)
    
    print("\n생성된 커밋 메시지:")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(message)
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

