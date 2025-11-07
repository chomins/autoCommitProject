#!/usr/bin/env python3
"""
Auto Commit - AI 기반 자동 커밋 도구
하루 개발 내용을 분석하여 자동으로 커밋 메시지를 생성하고 커밋합니다.
"""

import sys
import argparse
from typing import List, Optional
from pathlib import Path

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.prompt import Confirm, Prompt
    from rich.table import Table
    from rich.progress import Progress, SpinnerColumn, TextColumn
except ImportError:
    print("Error: rich 라이브러리가 설치되지 않았습니다.")
    print("다음 명령어를 실행하세요: pip install -r requirements.txt")
    sys.exit(1)

from git_analyzer import GitAnalyzer, GitChanges
from commit_message_generator import CommitMessageGenerator
from config_manager import ConfigManager
from code_reviewer import CodeReviewer, ReviewLevel


console = Console()


def print_changes_summary(changes: GitChanges):
    """변경사항 요약 출력"""
    table = Table(title="📊 변경사항 요약")
    table.add_column("항목", style="cyan")
    table.add_column("값", style="green")
    
    table.add_row("Staged 파일", str(len(changes.staged_files)))
    table.add_row("Unstaged 파일", str(len(changes.unstaged_files)))
    table.add_row("총 파일", str(changes.total_files))
    table.add_row("삽입", f"+{changes.total_insertions} 줄", style="green")
    table.add_row("삭제", f"-{changes.total_deletions} 줄", style="red")
    
    console.print(table)


def print_file_list(changes: GitChanges):
    """변경된 파일 목록 출력"""
    if changes.staged_files:
        console.print("\n[bold cyan]Staged 파일:[/bold cyan]")
        for f in changes.staged_files:
            change_type_symbol = {
                'A': '[green]+[/green]',
                'M': '[yellow]M[/yellow]',
                'D': '[red]-[/red]',
                'R': '[blue]R[/blue]'
            }.get(f.change_type, '?')
            console.print(f"  {change_type_symbol} {f.path} [dim](+{f.insertions}/-{f.deletions})[/dim]")
    
    if changes.unstaged_files:
        console.print("\n[bold yellow]Unstaged 파일:[/bold yellow]")
        for f in changes.unstaged_files:
            change_type_symbol = {
                'A': '[green]+[/green]',
                'M': '[yellow]M[/yellow]',
                'D': '[red]-[/red]',
                'R': '[blue]R[/blue]'
            }.get(f.change_type, '?')
            console.print(f"  {change_type_symbol} {f.path} [dim](+{f.insertions}/-{f.deletions})[/dim]")


def print_commit_message(message: str):
    """커밋 메시지 출력"""
    console.print(
        Panel(
            message,
            title="🤖 생성된 커밋 메시지",
            border_style="green",
            padding=(1, 2)
        )
    )


def print_code_review(review: str, token_estimate: int):
    """코드 리뷰 결과 출력"""
    console.print(
        Panel(
            review,
            title="🔍 AI 코드 리뷰",
            border_style="cyan",
            padding=(1, 2)
        )
    )
    console.print(f"[dim]💡 예상 토큰 사용: ~{token_estimate} tokens[/dim]\n")


def main():
    parser = argparse.ArgumentParser(
        description="AI 기반 자동 커밋 도구",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예제:
  python auto_commit.py                    # 기본 실행
  python auto_commit.py --staged-only      # Staged 파일만 커밋
  python auto_commit.py --dry-run          # 커밋 메시지만 생성
  python auto_commit.py --auto-yes         # 확인 없이 자동 커밋
  python auto_commit.py --files src/*.py   # 특정 파일만 커밋
  python auto_commit.py --review           # 코드 리뷰 포함 (간단)
  python auto_commit.py --review-detailed  # 코드 리뷰 포함 (상세)
        """
    )
    
    parser.add_argument(
        '--files',
        nargs='+',
        help='커밋할 파일 목록 (지정하지 않으면 모든 변경사항)'
    )
    
    parser.add_argument(
        '--staged-only',
        action='store_true',
        help='Staged된 파일만 커밋'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='커밋 메시지만 생성하고 실제 커밋은 하지 않음'
    )
    
    parser.add_argument(
        '--auto-yes',
        action='store_true',
        help='확인 없이 자동으로 커밋 (주의!)'
    )
    
    parser.add_argument(
        '--config',
        default='config.yaml',
        help='설정 파일 경로 (기본: config.yaml)'
    )
    
    parser.add_argument(
        '--no-add',
        action='store_true',
        help='자동으로 파일을 staging하지 않음'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='상세 정보 출력'
    )
    
    parser.add_argument(
        '--review',
        action='store_true',
        help='커밋 전에 코드 리뷰 수행 (config.yaml에서 기본값 설정 가능)'
    )
    
    parser.add_argument(
        '--no-review',
        action='store_true',
        help='코드 리뷰 건너뛰기 (config에서 enabled=true인 경우)'
    )
    
    parser.add_argument(
        '--review-level',
        choices=['quick', 'normal', 'detailed'],
        default=None,
        help='리뷰 상세 수준 (quick: 최소, normal: 중간, detailed: 상세)'
    )
    
    parser.add_argument(
        '--review-detailed',
        action='store_true',
        help='상세 코드 리뷰 수행 (--review --review-level detailed와 동일)'
    )
    
    parser.add_argument(
        '--review-only',
        action='store_true',
        help='리뷰만 수행하고 커밋하지 않음'
    )
    
    args = parser.parse_args()
    
    try:
        # 설정 로드
        console.print("[bold blue]⚙️  설정 로드 중...[/bold blue]")
        config = ConfigManager(config_path=args.config)
        
        if not config.validate():
            console.print("[bold red]❌ 설정이 유효하지 않습니다.[/bold red]")
            sys.exit(1)
        
        if args.verbose:
            config.print_config()
        
        # Git 저장소 분석
        console.print("\n[bold blue]📊 Git 변경사항 분석 중...[/bold blue]")
        analyzer = GitAnalyzer()
        
        if not analyzer.has_changes():
            console.print("[yellow]변경사항이 없습니다.[/yellow]")
            sys.exit(0)
        
        # 변경사항 가져오기
        changes = analyzer.get_all_changes(include_untracked=not args.staged_only)
        
        # 특정 파일만 선택
        if args.files:
            # 파일 필터링
            file_set = set(args.files)
            changes.staged_files = [f for f in changes.staged_files if f.path in file_set]
            changes.unstaged_files = [f for f in changes.unstaged_files if f.path in file_set]
            changes.total_files = len(changes.staged_files) + len(changes.unstaged_files)
        
        if changes.total_files == 0:
            console.print("[yellow]커밋할 변경사항이 없습니다.[/yellow]")
            sys.exit(0)
        
        # 변경사항 요약 출력
        print_changes_summary(changes)
        print_file_list(changes)
        
        # Unstaged 파일 처리
        if changes.unstaged_files and not args.staged_only:
            auto_add = config.get('git.auto_add', False) and not args.no_add
            
            if auto_add:
                console.print("\n[yellow]⚠️  Unstaged 파일을 자동으로 staging합니다.[/yellow]")
                analyzer.stage_file_changes(changes.unstaged_files)
            else:
                if not args.auto_yes:
                    add_files = Confirm.ask("\nUnstaged 파일을 staging하시겠습니까?")
                    if add_files:
                        analyzer.stage_file_changes(changes.unstaged_files)
                        console.print("[green]✅ 파일이 staging되었습니다.[/green]")
                    else:
                        console.print("[yellow]Staged된 파일만 커밋합니다.[/yellow]")
                        changes.unstaged_files = []
                else:
                    console.print("[yellow]⚠️  --auto-yes 옵션으로 인해 unstaged 파일은 제외됩니다.[/yellow]")
                    changes.unstaged_files = []
        
        # 커밋할 파일 목록
        files_to_commit = changes.staged_files + changes.unstaged_files
        
        if not files_to_commit:
            console.print("[yellow]커밋할 파일이 없습니다.[/yellow]")
            sys.exit(0)
        
        # AI 제공자 가져오기 (리뷰 및 커밋 메시지 생성에 사용)
        provider = config.get_ai_provider()
        
        # 코드 리뷰 수행 여부 결정
        review_enabled = config.get('review', {}).get('enabled', False)
        should_review = (
            args.review or 
            args.review_detailed or 
            args.review_only or 
            (review_enabled and not args.no_review)
        )
        
        # 코드 리뷰 수행
        review_result = None
        if should_review:
            console.print("\n[bold cyan]🔍 AI 코드 리뷰 수행 중...[/bold cyan]")
            
            # 리뷰 레벨 결정
            if args.review_detailed:
                review_level = ReviewLevel.DETAILED
            elif args.review_level:
                review_level = args.review_level
            else:
                # config에서 기본 레벨 가져오기
                default_level = config.get('review', {}).get('default_level', 'quick')
                review_level = default_level
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task(f"코드 분석 중 ({review_level} 모드)...", total=None)
                
                try:
                    reviewer = CodeReviewer(
                        provider=provider,
                        api_key=config.get_api_key(provider)
                    )
                    
                    review_result = reviewer.review(
                        files_to_commit,
                        config.to_dict(),
                        level=review_level
                    )
                    
                    progress.update(task, completed=True)
                except Exception as e:
                    console.print(f"\n[bold yellow]⚠️  코드 리뷰 실패: {e}[/bold yellow]")
                    if not args.review_only:
                        console.print("[yellow]리뷰 없이 계속 진행합니다...[/yellow]")
                    else:
                        sys.exit(1)
            
            # 리뷰 결과 출력
            if review_result:
                console.print()
                print_code_review(
                    review_result['review'],
                    review_result['token_estimate']
                )
            
            # 리뷰만 수행하는 모드
            if args.review_only:
                console.print("[cyan]리뷰만 수행했습니다. 커밋하지 않습니다.[/cyan]")
                sys.exit(0)
        
        # AI 커밋 메시지 생성
        console.print("\n[bold blue]🤖 AI 커밋 메시지 생성 중...[/bold blue]")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task(f"{provider.upper()} API 호출 중...", total=None)
            
            try:
                generator = CommitMessageGenerator(
                    provider=provider,
                    api_key=config.get_api_key(provider)
                )
                
                commit_message = generator.generate(files_to_commit, config.to_dict())
                
                progress.update(task, completed=True)
            except Exception as e:
                console.print(f"\n[bold red]❌ 커밋 메시지 생성 실패: {e}[/bold red]")
                sys.exit(1)
        
        # 커밋 메시지 출력
        console.print()
        print_commit_message(commit_message)
        
        # Dry run 모드
        if args.dry_run:
            console.print("\n[yellow]🔍 Dry-run 모드: 커밋하지 않습니다.[/yellow]")
            sys.exit(0)
        
        # 커밋 확인
        if args.auto_yes:
            do_commit = True
        else:
            console.print()
            choice = Prompt.ask(
                "이 메시지로 커밋하시겠습니까?",
                choices=["y", "n", "e"],
                default="y"
            )
            
            if choice == "e":
                # 메시지 편집
                console.print("\n[cyan]커밋 메시지를 입력하세요 (빈 줄로 끝):[/cyan]")
                lines = []
                while True:
                    try:
                        line = input()
                        if line == "" and lines:
                            break
                        lines.append(line)
                    except EOFError:
                        break
                
                commit_message = "\n".join(lines)
                
                if not commit_message.strip():
                    console.print("[red]커밋 메시지가 비어있습니다. 커밋을 취소합니다.[/red]")
                    sys.exit(1)
                
                do_commit = True
            elif choice == "y":
                do_commit = True
            else:
                do_commit = False
        
        if do_commit:
            try:
                # 커밋 실행
                commit = analyzer.commit(commit_message)
                console.print(f"\n[bold green]✅ 커밋 완료! [{commit.hexsha[:7]}][/bold green]")
                console.print(f"[dim]{commit.message.strip()}[/dim]")
            except Exception as e:
                console.print(f"\n[bold red]❌ 커밋 실패: {e}[/bold red]")
                sys.exit(1)
        else:
            console.print("\n[yellow]커밋이 취소되었습니다.[/yellow]")
            sys.exit(0)
    
    except KeyboardInterrupt:
        console.print("\n\n[yellow]사용자에 의해 중단되었습니다.[/yellow]")
        sys.exit(130)
    except Exception as e:
        console.print(f"\n[bold red]❌ 오류 발생: {e}[/bold red]")
        if args.verbose:
            import traceback
            console.print(traceback.format_exc())
        sys.exit(1)


if __name__ == "__main__":
    main()

