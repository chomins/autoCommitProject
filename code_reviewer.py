"""
AI 기반 코드 리뷰어
토큰을 최소화하면서 효과적인 코드 리뷰를 제공합니다.
"""

import os
from typing import List, Dict, Optional
from abc import ABC, abstractmethod
from git_analyzer import FileChange


class ReviewLevel:
    """리뷰 상세 수준"""
    QUICK = "quick"        # 50-100 토큰: 명백한 버그, 심각한 문제만
    NORMAL = "normal"      # 200-300 토큰: 로직, 잠재적 이슈
    DETAILED = "detailed"  # 500+ 토큰: 전체 분석 (아키텍처, 성능, 보안)


class AIReviewProvider(ABC):
    """AI 리뷰 제공자 추상 클래스"""
    
    @abstractmethod
    def review_code(self, compressed_diff: str, level: str, config: dict) -> str:
        """코드 리뷰 수행"""
        pass


class OpenAIReviewProvider(AIReviewProvider):
    """OpenAI 리뷰 제공자"""
    
    def __init__(self, api_key: str):
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=api_key)
        except ImportError:
            raise ImportError("OpenAI 라이브러리가 설치되지 않았습니다.")
    
    def review_code(self, compressed_diff: str, level: str, config: dict) -> str:
        """OpenAI를 사용하여 코드 리뷰"""
        prompt = self._build_prompt(compressed_diff, level)
        
        model = config.get('ai', {}).get('model', 'gpt-4')
        temperature = config.get('review', {}).get('temperature', 0.2)
        max_tokens = self._get_max_tokens(level, config)
        
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert code reviewer. Provide concise, actionable feedback."
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
    
    def _build_prompt(self, compressed_diff: str, level: str) -> str:
        """리뷰 프롬프트 생성"""
        if level == ReviewLevel.QUICK:
            return self._quick_review_prompt(compressed_diff)
        elif level == ReviewLevel.DETAILED:
            return self._detailed_review_prompt(compressed_diff)
        else:
            return self._normal_review_prompt(compressed_diff)
    
    def _quick_review_prompt(self, diff: str) -> str:
        """간단 리뷰 프롬프트 (토큰 최소화)"""
        return f"""Quick code review - ONLY report critical issues:

Code changes:
{diff}

Focus on:
❌ Bugs (null pointer, logic errors)
⚠️  Security issues
🔥 Performance problems

Format (Korean):
- Use ✅/⚠️/❌ symbols
- Max 3 items
- Be specific and brief

If no issues: "✅ 문제 없음"
"""
    
    def _normal_review_prompt(self, diff: str) -> str:
        """일반 리뷰 프롬프트"""
        return f"""Code review - balanced detail:

Code changes:
{diff}

Review:
❌ Critical: bugs, security
⚠️  Warning: potential issues, edge cases
💡 Suggestion: code quality, naming

Format (Korean):
- Group by severity
- Be specific with line context
- Max 5-7 items total

If mostly good: "✅ 전반적으로 양호합니다" + any warnings
"""
    
    def _detailed_review_prompt(self, diff: str) -> str:
        """상세 리뷰 프롬프트"""
        return f"""Detailed code review:

Code changes:
{diff}

Analyze:
🐛 Bugs & Logic errors
🔒 Security vulnerabilities
⚡ Performance issues
🏗️  Architecture & design patterns
📝 Code quality & readability
✨ Best practices

Format (Korean):
- Organized by category
- Specific examples with context
- Actionable recommendations

Provide thorough analysis.
"""
    
    def _get_max_tokens(self, level: str, config: dict) -> int:
        """레벨별 최대 토큰 수"""
        review_config = config.get('review', {})
        
        if level == ReviewLevel.QUICK:
            return review_config.get('max_tokens_quick', 150)
        elif level == ReviewLevel.DETAILED:
            return review_config.get('max_tokens_detailed', 800)
        else:
            return review_config.get('max_tokens_normal', 400)


class GeminiReviewProvider(AIReviewProvider):
    """Google Gemini 리뷰 제공자"""
    
    def __init__(self, api_key: str):
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            self.genai = genai
        except ImportError:
            raise ImportError("Google Generative AI 라이브러리가 설치되지 않았습니다.")
    
    def review_code(self, compressed_diff: str, level: str, config: dict) -> str:
        """Gemini를 사용하여 코드 리뷰"""
        prompt = self._build_prompt(compressed_diff, level)
        
        model_name = config.get('ai', {}).get('model', 'gemini-2.0-flash')
        temperature = config.get('review', {}).get('temperature', 0.2)
        max_tokens = self._get_max_tokens(level, config)
        
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
    
    def _build_prompt(self, compressed_diff: str, level: str) -> str:
        """리뷰 프롬프트 생성"""
        if level == ReviewLevel.QUICK:
            return self._quick_review_prompt(compressed_diff)
        elif level == ReviewLevel.DETAILED:
            return self._detailed_review_prompt(compressed_diff)
        else:
            return self._normal_review_prompt(compressed_diff)
    
    def _quick_review_prompt(self, diff: str) -> str:
        """간단 리뷰 프롬프트"""
        return f"""Quick code review - ONLY report critical issues:

Code changes:
{diff}

Focus on:
❌ Bugs (null pointer, logic errors)
⚠️  Security issues
🔥 Performance problems

Format (Korean):
- Use ✅/⚠️/❌ symbols
- Max 3 items
- Be specific and brief

If no issues: "✅ 문제 없음"
"""
    
    def _normal_review_prompt(self, diff: str) -> str:
        """일반 리뷰 프롬프트"""
        return f"""Code review - balanced detail:

Code changes:
{diff}

Review:
❌ Critical: bugs, security
⚠️  Warning: potential issues, edge cases
💡 Suggestion: code quality, naming

Format (Korean):
- Group by severity
- Be specific with line context
- Max 5-7 items total

If mostly good: "✅ 전반적으로 양호합니다" + any warnings
"""
    
    def _detailed_review_prompt(self, diff: str) -> str:
        """상세 리뷰 프롬프트"""
        return f"""Detailed code review:

Code changes:
{diff}

Analyze:
🐛 Bugs & Logic errors
🔒 Security vulnerabilities
⚡ Performance issues
🏗️  Architecture & design patterns
📝 Code quality & readability
✨ Best practices

Format (Korean):
- Organized by category
- Specific examples with context
- Actionable recommendations

Provide thorough analysis.
"""
    
    def _get_max_tokens(self, level: str, config: dict) -> int:
        """레벨별 최대 토큰 수"""
        review_config = config.get('review', {})
        
        if level == ReviewLevel.QUICK:
            return review_config.get('max_tokens_quick', 150)
        elif level == ReviewLevel.DETAILED:
            return review_config.get('max_tokens_detailed', 800)
        else:
            return review_config.get('max_tokens_normal', 400)


class AnthropicReviewProvider(AIReviewProvider):
    """Anthropic (Claude) 리뷰 제공자"""
    
    def __init__(self, api_key: str):
        try:
            import anthropic
            self.client = anthropic.Anthropic(api_key=api_key)
        except ImportError:
            raise ImportError("Anthropic 라이브러리가 설치되지 않았습니다.")
    
    def review_code(self, compressed_diff: str, level: str, config: dict) -> str:
        """Claude를 사용하여 코드 리뷰"""
        prompt = self._build_prompt(compressed_diff, level)
        
        model = config.get('ai', {}).get('model', 'claude-3-sonnet-20240229')
        temperature = config.get('review', {}).get('temperature', 0.2)
        max_tokens = self._get_max_tokens(level, config)
        
        try:
            response = self.client.messages.create(
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                system="You are an expert code reviewer. Provide concise, actionable feedback.",
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
    
    def _build_prompt(self, compressed_diff: str, level: str) -> str:
        """리뷰 프롬프트 생성"""
        if level == ReviewLevel.QUICK:
            return self._quick_review_prompt(compressed_diff)
        elif level == ReviewLevel.DETAILED:
            return self._detailed_review_prompt(compressed_diff)
        else:
            return self._normal_review_prompt(compressed_diff)
    
    def _quick_review_prompt(self, diff: str) -> str:
        """간단 리뷰 프롬프트"""
        return f"""Quick code review - ONLY report critical issues:

Code changes:
{diff}

Focus on:
❌ Bugs (null pointer, logic errors)
⚠️  Security issues
🔥 Performance problems

Format (Korean):
- Use ✅/⚠️/❌ symbols
- Max 3 items
- Be specific and brief

If no issues: "✅ 문제 없음"
"""
    
    def _normal_review_prompt(self, diff: str) -> str:
        """일반 리뷰 프롬프트"""
        return f"""Code review - balanced detail:

Code changes:
{diff}

Review:
❌ Critical: bugs, security
⚠️  Warning: potential issues, edge cases
💡 Suggestion: code quality, naming

Format (Korean):
- Group by severity
- Be specific with line context
- Max 5-7 items total

If mostly good: "✅ 전반적으로 양호합니다" + any warnings
"""
    
    def _detailed_review_prompt(self, diff: str) -> str:
        """상세 리뷰 프롬프트"""
        return f"""Detailed code review:

Code changes:
{diff}

Analyze:
🐛 Bugs & Logic errors
🔒 Security vulnerabilities
⚡ Performance issues
🏗️  Architecture & design patterns
📝 Code quality & readability
✨ Best practices

Format (Korean):
- Organized by category
- Specific examples with context
- Actionable recommendations

Provide thorough analysis.
"""
    
    def _get_max_tokens(self, level: str, config: dict) -> int:
        """레벨별 최대 토큰 수"""
        review_config = config.get('review', {})
        
        if level == ReviewLevel.QUICK:
            return review_config.get('max_tokens_quick', 150)
        elif level == ReviewLevel.DETAILED:
            return review_config.get('max_tokens_detailed', 800)
        else:
            return review_config.get('max_tokens_normal', 400)


class DiffCompressor:
    """Diff 압축기 - 토큰 사용량을 최소화"""
    
    @staticmethod
    def compress(changes: List[FileChange], level: str) -> str:
        """변경사항을 압축하여 핵심만 추출"""
        compressed_parts = []
        total_lines = sum(c.insertions + c.deletions for c in changes)
        
        # 변경사항 크기에 따라 자동 조절
        if total_lines > 500 and level != ReviewLevel.DETAILED:
            # 대량 변경: 요약만
            return DiffCompressor._compress_summary(changes)
        elif total_lines > 200 and level == ReviewLevel.QUICK:
            # 중간 변경 + quick: 매우 간단하게
            return DiffCompressor._compress_minimal(changes)
        else:
            # 일반적인 압축
            return DiffCompressor._compress_smart(changes, level)
    
    @staticmethod
    def _compress_summary(changes: List[FileChange]) -> str:
        """대량 변경사항 요약"""
        summary = "⚠️  대량 변경 감지 - 요약 리뷰\n\n"
        
        by_type = {}
        for change in changes:
            ext = change.path.split('.')[-1] if '.' in change.path else 'other'
            if ext not in by_type:
                by_type[ext] = []
            by_type[ext].append(change)
        
        for ext, files in by_type.items():
            total_add = sum(f.insertions for f in files)
            total_del = sum(f.deletions for f in files)
            summary += f"📁 .{ext} 파일: {len(files)}개 (+{total_add}/-{total_del})\n"
            
            # 가장 큰 변경사항 2개만
            sorted_files = sorted(files, key=lambda f: f.insertions + f.deletions, reverse=True)
            for f in sorted_files[:2]:
                summary += f"  • {f.path} (+{f.insertions}/-{f.deletions})\n"
        
        return summary
    
    @staticmethod
    def _compress_minimal(changes: List[FileChange]) -> str:
        """최소 압축 (파일 목록과 주요 변경만)"""
        result = "📝 변경 파일:\n"
        
        for change in changes:
            result += f"\n• {change.path} ({change.change_type}) +{change.insertions}/-{change.deletions}\n"
            
            # 핵심 변경만 추출
            key_changes = DiffCompressor._extract_key_changes(change.diff, limit=5)
            if key_changes:
                result += "  핵심 변경:\n"
                for line in key_changes:
                    result += f"    {line}\n"
        
        return result
    
    @staticmethod
    def _compress_smart(changes: List[FileChange], level: str) -> str:
        """스마트 압축 - 중요한 부분만"""
        result = ""
        
        for change in changes:
            # 파일 우선순위
            priority = DiffCompressor._get_file_priority(change.path)
            
            if priority == "low" and level == ReviewLevel.QUICK:
                # 저우선순위 파일은 quick 모드에서 스킵
                continue
            
            result += f"\n━━━ {change.path} ({change.change_type}) +{change.insertions}/-{change.deletions}\n"
            
            # diff 압축
            if change.diff:
                compressed_diff = DiffCompressor._compress_diff_content(
                    change.diff,
                    level,
                    change.change_type
                )
                result += compressed_diff + "\n"
        
        return result
    
    @staticmethod
    def _get_file_priority(path: str) -> str:
        """파일 우선순위 결정"""
        # 낮은 우선순위
        low_priority_patterns = [
            'test_', '_test.', '.test.',
            'spec.', '.spec.',
            'config.', 'setup.', 'requirements.',
            '.md', '.txt', '.yml', '.yaml', '.json',
            'migration', '__init__'
        ]
        
        path_lower = path.lower()
        for pattern in low_priority_patterns:
            if pattern in path_lower:
                return "low"
        
        # 높은 우선순위 (API, 서비스, 모델 등)
        high_priority_patterns = [
            'service', 'controller', 'api', 'model',
            'handler', 'middleware', 'auth', 'security'
        ]
        
        for pattern in high_priority_patterns:
            if pattern in path_lower:
                return "high"
        
        return "normal"
    
    @staticmethod
    def _compress_diff_content(diff: str, level: str, change_type: str) -> str:
        """diff 내용 압축"""
        lines = diff.split('\n')
        result = []
        
        # 새 파일은 시그니처만
        if change_type == 'A':
            signatures = DiffCompressor._extract_signatures(lines)
            if signatures:
                result.append("새로운 정의:")
                result.extend(signatures[:15 if level == ReviewLevel.DETAILED else 8])
            else:
                # 시그니처가 없으면 주요 라인만
                key_lines = DiffCompressor._extract_key_changes(diff, limit=10)
                result.extend(key_lines)
        else:
            # 수정/삭제 파일
            additions = []
            deletions = []
            context_lines = []
            
            for i, line in enumerate(lines):
                if line.startswith('+') and not line.startswith('+++'):
                    clean_line = line[1:].strip()
                    if DiffCompressor._is_important_line(clean_line):
                        additions.append(f"+ {clean_line[:100]}")
                        
                elif line.startswith('-') and not line.startswith('---'):
                    clean_line = line[1:].strip()
                    if DiffCompressor._is_important_line(clean_line):
                        deletions.append(f"- {clean_line[:100]}")
            
            # 제한
            max_lines = 20 if level == ReviewLevel.DETAILED else 10
            
            if deletions:
                result.append("제거됨:")
                result.extend(deletions[:max_lines // 2])
            
            if additions:
                result.append("추가됨:")
                result.extend(additions[:max_lines // 2])
        
        return '\n'.join(result[:30])  # 최대 30줄
    
    @staticmethod
    def _extract_signatures(lines: List[str]) -> List[str]:
        """함수/클래스 시그니처 추출"""
        signatures = []
        keywords = ['def ', 'class ', 'function ', 'const ', 'let ', 'var ',
                   'public ', 'private ', 'protected ', 'async ', '@']
        
        for line in lines:
            clean = line.lstrip('+').strip()
            if any(kw in clean for kw in keywords):
                if '(' in clean or 'class ' in clean:
                    signatures.append(clean[:120])
        
        return signatures
    
    @staticmethod
    def _extract_key_changes(diff: str, limit: int = 10) -> List[str]:
        """핵심 변경사항만 추출"""
        lines = diff.split('\n')
        key_lines = []
        
        for line in lines:
            if line.startswith('+') and not line.startswith('+++'):
                clean = line[1:].strip()
                if DiffCompressor._is_important_line(clean):
                    key_lines.append(f"+ {clean[:100]}")
                    if len(key_lines) >= limit:
                        break
        
        return key_lines
    
    @staticmethod
    def _is_important_line(line: str) -> bool:
        """중요한 라인인지 판단"""
        if not line or len(line) < 3:
            return False
        
        # 제외할 패턴
        skip_patterns = [
            'import ', 'from ', '#', '//', '/*', '*/',
            '{', '}', '(', ')', '[', ']', ';',
            '"""', "'''", 'pass', 'console.log'
        ]
        
        line_lower = line.lower().strip()
        for pattern in skip_patterns:
            if line_lower.startswith(pattern) or line_lower == pattern:
                return False
        
        # 중요한 패턴
        important_patterns = [
            'def ', 'class ', 'function ', 'return ',
            'if ', 'else', 'for ', 'while ', 'try', 'catch',
            '=', 'await ', 'async ', '@'
        ]
        
        return any(pattern in line for pattern in important_patterns)


class CodeReviewer:
    """코드 리뷰어 메인 클래스"""
    
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
            self.provider = OpenAIReviewProvider(api_key)
        elif provider == "anthropic":
            self.provider = AnthropicReviewProvider(api_key)
        elif provider == "gemini":
            self.provider = GeminiReviewProvider(api_key)
        else:
            raise ValueError(f"지원하지 않는 provider: {provider}")
    
    def review(
        self,
        changes: List[FileChange],
        config: dict,
        level: str = ReviewLevel.QUICK
    ) -> Dict[str, any]:
        """
        코드 리뷰 수행
        
        Args:
            changes: 변경사항 목록
            config: 설정
            level: 리뷰 레벨 (quick/normal/detailed)
        
        Returns:
            리뷰 결과 및 토큰 사용량 정보
        """
        if not changes:
            return {
                'review': '✅ 변경사항이 없습니다.',
                'token_estimate': 0
            }
        
        # diff 압축
        compressed_diff = DiffCompressor.compress(changes, level)
        
        # 토큰 추정 (대략적)
        token_estimate = len(compressed_diff) // 4  # 평균 4자 = 1토큰
        
        # AI 리뷰 수행
        try:
            review_text = self.provider.review_code(compressed_diff, level, config)
            
            return {
                'review': review_text,
                'compressed_diff': compressed_diff,
                'token_estimate': token_estimate,
                'level': level
            }
        except Exception as e:
            raise RuntimeError(f"코드 리뷰 실패: {e}")


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
    
    print(f"🔍 {provider.upper()}를 사용하여 코드 리뷰 중...\n")
    
    # 코드 리뷰
    reviewer = CodeReviewer(provider=provider)
    result = reviewer.review(all_changes, config, level=ReviewLevel.QUICK)
    
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("🤖 AI 코드 리뷰")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(result['review'])
    print(f"\n💡 예상 토큰 사용량: ~{result['token_estimate']} tokens")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

