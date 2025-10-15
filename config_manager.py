"""
설정 파일 및 환경 변수 관리 모듈
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv


class ConfigManager:
    """설정 관리자"""
    
    DEFAULT_CONFIG = {
        'commit': {
            'max_subject_length': 72,
            'include_file_list': True,
            'conventional_commits': True,
            'types': ['feat', 'fix', 'docs', 'style', 'refactor', 'test', 'chore', 'perf', 'ci', 'build']
        },
        'ai': {
            'model': 'gpt-4',
            'temperature': 0.3,
            'max_tokens': 500
        },
        'git': {
            'auto_add': False,
            'exclude_patterns': ['*.log', '*.tmp', '.env', '__pycache__/']
        }
    }
    
    def __init__(self, config_path: Optional[str] = None, env_path: Optional[str] = None):
        """
        Args:
            config_path: config.yaml 파일 경로
            env_path: .env 파일 경로
        """
        # .env 파일 로드 (우선순위: 1. 지정된 경로, 2. 현재 디렉토리, 3. ~/.auto-commit/)
        if env_path and Path(env_path).exists():
            load_dotenv(env_path)
        elif Path('.env').exists():
            load_dotenv('.env')
        else:
            # 홈 디렉토리의 전역 설정 찾기
            home_env = Path.home() / '.auto-commit' / '.env'
            if home_env.exists():
                load_dotenv(home_env)
            else:
                load_dotenv()
        
        # config.yaml 로드 (우선순위: 1. 지정된 경로, 2. 현재 디렉토리, 3. ~/.auto-commit/)
        if config_path:
            self.config_path = config_path
        elif Path('config.yaml').exists():
            self.config_path = 'config.yaml'
        elif Path('.auto-commit.yaml').exists():
            self.config_path = '.auto-commit.yaml'
        else:
            home_config = Path.home() / '.auto-commit' / 'config.yaml'
            if home_config.exists():
                self.config_path = str(home_config)
            else:
                self.config_path = 'config.yaml'
        
        self.config = self._load_config()
        
        # 환경 변수 오버라이드
        self._apply_env_overrides()
    
    def _load_config(self) -> Dict[str, Any]:
        """config.yaml 파일 로드"""
        if Path(self.config_path).exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)
                    
                # 기본 설정과 병합
                return self._merge_configs(self.DEFAULT_CONFIG, config or {})
            except Exception as e:
                print(f"Warning: config.yaml 로드 실패, 기본 설정 사용: {e}")
                return self.DEFAULT_CONFIG.copy()
        else:
            print(f"Warning: {self.config_path} 파일이 없습니다. 기본 설정을 사용합니다.")
            return self.DEFAULT_CONFIG.copy()
    
    def _merge_configs(self, default: Dict, override: Dict) -> Dict:
        """설정 병합 (재귀적)"""
        result = default.copy()
        
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def _apply_env_overrides(self):
        """환경 변수로 설정 오버라이드"""
        # AI 모델
        if os.getenv('AI_MODEL'):
            self.config['ai']['model'] = os.getenv('AI_MODEL')
        
        # Temperature
        if os.getenv('AI_TEMPERATURE'):
            try:
                self.config['ai']['temperature'] = float(os.getenv('AI_TEMPERATURE'))
            except ValueError:
                pass
        
        # Max tokens
        if os.getenv('AI_MAX_TOKENS'):
            try:
                self.config['ai']['max_tokens'] = int(os.getenv('AI_MAX_TOKENS'))
            except ValueError:
                pass
    
    def get(self, key: str, default: Any = None) -> Any:
        """설정 값 가져오기 (점 표기법 지원)"""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def get_ai_provider(self) -> str:
        """AI 제공자 가져오기"""
        provider = os.getenv('AI_PROVIDER', 'openai').lower()
        
        if provider not in ['openai', 'anthropic', 'gemini']:
            print(f"Warning: 지원하지 않는 AI_PROVIDER '{provider}', 'openai' 사용")
            return 'openai'
        
        return provider
    
    def get_api_key(self, provider: Optional[str] = None) -> str:
        """API 키 가져오기"""
        if provider is None:
            provider = self.get_ai_provider()
        
        if provider == 'openai':
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                raise ValueError(
                    "OPENAI_API_KEY 환경 변수가 설정되지 않았습니다.\n"
                    ".env 파일을 생성하고 API 키를 설정하세요."
                )
        elif provider == 'anthropic':
            api_key = os.getenv('ANTHROPIC_API_KEY')
            if not api_key:
                raise ValueError(
                    "ANTHROPIC_API_KEY 환경 변수가 설정되지 않았습니다.\n"
                    ".env 파일을 생성하고 API 키를 설정하세요."
                )
        elif provider == 'gemini':
            api_key = os.getenv('GOOGLE_API_KEY')
            if not api_key:
                raise ValueError(
                    "GOOGLE_API_KEY 환경 변수가 설정되지 않았습니다.\n"
                    ".env 파일을 생성하고 API 키를 설정하세요."
                )
        else:
            raise ValueError(f"지원하지 않는 provider: {provider}")
        
        return api_key
    
    def validate(self) -> bool:
        """설정 유효성 검사"""
        try:
            # AI 제공자 확인
            provider = self.get_ai_provider()
            
            # API 키 확인
            self.get_api_key(provider)
            
            # 설정 값 확인
            if self.config['ai']['temperature'] < 0 or self.config['ai']['temperature'] > 1:
                print("Warning: temperature는 0과 1 사이여야 합니다.")
                return False
            
            if self.config['ai']['max_tokens'] <= 0:
                print("Warning: max_tokens는 양수여야 합니다.")
                return False
            
            if self.config['commit']['max_subject_length'] <= 0:
                print("Warning: max_subject_length는 양수여야 합니다.")
                return False
            
            return True
            
        except Exception as e:
            print(f"설정 유효성 검사 실패: {e}")
            return False
    
    def to_dict(self) -> Dict[str, Any]:
        """설정을 딕셔너리로 반환"""
        return self.config.copy()
    
    def print_config(self):
        """설정 출력 (디버깅용)"""
        print("현재 설정:")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"AI Provider: {self.get_ai_provider()}")
        print(f"AI Model: {self.config['ai']['model']}")
        print(f"Temperature: {self.config['ai']['temperature']}")
        print(f"Max Tokens: {self.config['ai']['max_tokens']}")
        print(f"Conventional Commits: {self.config['commit']['conventional_commits']}")
        print(f"Max Subject Length: {self.config['commit']['max_subject_length']}")
        print(f"Auto Add: {self.config['git']['auto_add']}")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")


if __name__ == "__main__":
    # 테스트 코드
    config = ConfigManager()
    
    if config.validate():
        print("✅ 설정이 유효합니다.")
        config.print_config()
    else:
        print("❌ 설정이 유효하지 않습니다.")

