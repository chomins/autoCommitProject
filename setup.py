"""
Auto Commit - AI 기반 자동 커밋 도구
전역 설치를 위한 setup.py
"""

from setuptools import setup, find_packages
from pathlib import Path

# README 읽기
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

setup(
    name="auto-commit-ai",
    version="1.0.0",
    author="Auto Commit",
    description="AI 기반 자동 Git 커밋 메시지 생성 도구",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/chomins/autoCommitProject",
    packages=find_packages(exclude=["tests*"]),
    py_modules=[
        "auto_commit",
        "git_analyzer",
        "commit_message_generator",
        "config_manager"
    ],
    install_requires=[
        "openai>=1.0.0",
        "anthropic>=0.25.0",
        "google-generativeai>=0.3.0",
        "python-dotenv>=1.0.0",
        "gitpython>=3.1.0",
        "pyyaml>=6.0",
        "rich>=13.0.0",
    ],
    entry_points={
        "console_scripts": [
            "auto-commit=auto_commit:main",
            "ac=auto_commit:main",  # 짧은 별칭
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Version Control :: Git",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.7",
    keywords="git commit ai openai anthropic claude gemini google automation",
    project_urls={
        "Bug Reports": "https://github.com/chomins/autoCommitProject/issues",
        "Source": "https://github.com/chomins/autoCommitProject",
    },
)

