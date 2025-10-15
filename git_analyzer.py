"""
Git 변경사항 분석 모듈
Git 저장소의 변경사항을 분석하고 diff 정보를 추출합니다.
"""

import git
from typing import List, Dict, Optional
from pathlib import Path
from dataclasses import dataclass


@dataclass
class FileChange:
    """파일 변경 정보"""
    path: str
    change_type: str  # 'A'(added), 'M'(modified), 'D'(deleted), 'R'(renamed)
    insertions: int
    deletions: int
    diff: str


@dataclass
class GitChanges:
    """Git 변경사항 정보"""
    staged_files: List[FileChange]
    unstaged_files: List[FileChange]
    total_insertions: int
    total_deletions: int
    total_files: int


class GitAnalyzer:
    """Git 저장소 분석기"""
    
    def __init__(self, repo_path: Optional[str] = None):
        """
        Args:
            repo_path: Git 저장소 경로 (None이면 현재 디렉토리)
        """
        self.repo_path = repo_path or "."
        try:
            self.repo = git.Repo(self.repo_path, search_parent_directories=True)
        except git.InvalidGitRepositoryError:
            raise ValueError(f"'{self.repo_path}'는 유효한 Git 저장소가 아닙니다.")
    
    def get_staged_changes(self) -> List[FileChange]:
        """Staged 변경사항 가져오기"""
        changes = []
        import os
        
        # git status --porcelain을 사용하여 정확한 상태 확인
        try:
            status_output = self.repo.git.status('--porcelain').split('\n')
            staged_files = {}
            
            for line in status_output:
                if len(line) < 4:
                    continue
                status_code = line[:2]
                file_path = line[3:]
                
                # staged 파일 (첫 번째 문자가 상태)
                first_char = status_code[0]
                if first_char in ['A', 'M', 'D', 'R']:
                    staged_files[file_path] = first_char
            
            print(f"🔍 Found {len(staged_files)} staged files from git status")
            
            # 각 staged 파일 처리
            for file_path, status in staged_files.items():
                try:
                    full_path = os.path.join(self.repo.working_dir, file_path.replace('/', os.sep))
                    
                    if status == 'A':  # 새 파일 추가
                        if os.path.exists(full_path):
                            with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                                content = f.read()
                            
                            diff_lines = [f'+{line}' for line in content.split('\n')]
                            diff_text = '\n'.join(diff_lines)
                            
                            changes.append(FileChange(
                                path=file_path,
                                change_type='A',
                                insertions=len(content.split('\n')),
                                deletions=0,
                                diff=diff_text
                            ))
                            print(f"  ✅ New file: {file_path} (+{len(content.split('\n'))} lines)")
                        
                    elif status == 'M':  # 수정된 파일
                        # git diff --cached로 실제 변경사항 가져오기
                        diff_output = self.repo.git.diff('--cached', file_path)
                        insertions, deletions = self._count_changes(diff_output)
                        
                        changes.append(FileChange(
                            path=file_path,
                            change_type='M',
                            insertions=insertions,
                            deletions=deletions,
                            diff=diff_output
                        ))
                        print(f"  ✅ Modified: {file_path} (+{insertions}/-{deletions} lines)")
                        
                    elif status == 'D':  # 삭제된 파일
                        diff_output = self.repo.git.diff('--cached', file_path)
                        insertions, deletions = self._count_changes(diff_output)
                        
                        changes.append(FileChange(
                            path=file_path,
                            change_type='D',
                            insertions=insertions,
                            deletions=deletions,
                            diff=diff_output
                        ))
                        print(f"  ✅ Deleted: {file_path} (+{insertions}/-{deletions} lines)")
                        
                except Exception as e:
                    print(f"Warning: Could not process {file_path}: {e}")
                    
        except Exception as e:
            print(f"Error getting staged changes: {e}")
            import traceback
            traceback.print_exc()
        
        return changes
    
    def get_unstaged_changes(self) -> List[FileChange]:
        """Unstaged 변경사항 가져오기 (git status + git diff 사용)"""
        changes = []
        
        try:
            # git status --porcelain으로 unstaged 파일 목록 가져오기
            import subprocess
            result = subprocess.run(
                ['git', 'status', '--porcelain'],
                cwd=self.repo.working_dir,
                capture_output=True,
                text=True,
                encoding='utf-8'
            )
            
            unstaged_files = []
            for line in result.stdout.splitlines():
                if len(line) < 4:
                    continue
                
                # 두 번째 문자가 변경 타입 (unstaged)
                status_code = line[1]
                file_path = line[3:].strip()
                
                # Unstaged 변경사항만 필터링 (M, D, A 등)
                if status_code in ['M', 'D', 'A'] and status_code != ' ':
                    unstaged_files.append((status_code, file_path))
            
            print(f"🔍 Found {len(unstaged_files)} unstaged files from git status")
            
            # 각 파일의 diff 가져오기
            for status_code, file_path in unstaged_files:
                try:
                    if status_code == 'M':
                        # 수정된 파일: git diff로 읽기
                        diff_result = subprocess.run(
                            ['git', 'diff', '--', file_path],
                            cwd=self.repo.working_dir,
                            capture_output=True,
                            text=True,
                            encoding='utf-8'
                        )
                        diff_text = diff_result.stdout
                        insertions, deletions = self._count_changes(diff_text)
                        print(f"  ✅ Modified: {file_path} (+{insertions}/-{deletions} lines)")
                        
                        changes.append(FileChange(
                            path=file_path,
                            change_type='M',
                            insertions=insertions,
                            deletions=deletions,
                            diff=diff_text
                        ))
                    
                    elif status_code == 'D':
                        # 삭제된 파일
                        diff_result = subprocess.run(
                            ['git', 'diff', '--', file_path],
                            cwd=self.repo.working_dir,
                            capture_output=True,
                            text=True,
                            encoding='utf-8'
                        )
                        diff_text = diff_result.stdout
                        insertions, deletions = self._count_changes(diff_text)
                        print(f"  ✅ Deleted: {file_path} (+{insertions}/-{deletions} lines)")
                        
                        changes.append(FileChange(
                            path=file_path,
                            change_type='D',
                            insertions=insertions,
                            deletions=deletions,
                            diff=diff_text
                        ))
                    
                    elif status_code == 'A':
                        # 새 파일 (untracked): 전체 내용 읽기
                        import os
                        full_path = os.path.join(self.repo.working_dir, file_path.replace('/', os.sep))
                        
                        if os.path.exists(full_path):
                            with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                                content = f.read()
                            
                            if content:
                                diff_lines = [f'+{line}' for line in content.split('\n')]
                                diff_text = '\n'.join(diff_lines)
                                insertions = len(content.split('\n'))
                                print(f"  ✅ New file: {file_path} (+{insertions} lines)")
                                
                                changes.append(FileChange(
                                    path=file_path,
                                    change_type='A',
                                    insertions=insertions,
                                    deletions=0,
                                    diff=diff_text
                                ))
                
                except Exception as e:
                    print(f"  ❌ Error processing {file_path}: {e}")
                    continue
        
        except Exception as e:
            print(f"❌ Error in get_unstaged_changes: {e}")
            import traceback
            traceback.print_exc()
        
        return changes
    
    def get_untracked_files(self) -> List[str]:
        """Untracked 파일 목록 가져오기"""
        return self.repo.untracked_files
    
    def _parse_diff_item(self, diff_item, is_new: bool = False) -> Optional[FileChange]:
        """Diff 항목 파싱"""
        try:
            # 변경 타입 결정
            if is_new or diff_item.new_file:
                change_type = 'A'
            elif diff_item.deleted_file:
                change_type = 'D'
            elif diff_item.renamed_file:
                change_type = 'R'
            else:
                change_type = 'M'
            
            # 파일 경로
            path = diff_item.b_path if diff_item.b_path else diff_item.a_path
            
            print(f"🔍 Parsing: {path} (type={change_type}, new_file={diff_item.new_file})")
            
            # 새 파일(A)은 무조건 파일에서 직접 읽기
            if change_type == 'A':
                try:
                    import os
                    full_path = os.path.join(self.repo.working_dir, path.replace('/', os.sep))
                    print(f"  → Trying to read: {full_path}")
                    print(f"  → File exists: {os.path.exists(full_path)}")
                    
                    if os.path.exists(full_path):
                        with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                        
                        print(f"  → File size: {len(content)} chars")
                        
                        if content:
                            # 전체 내용을 + 형태로 변환 (diff 형식)
                            diff_lines = [f'+{line}' for line in content.split('\n')]
                            diff_text = '\n'.join(diff_lines)
                            insertions = len(content.split('\n'))
                            deletions = 0
                            print(f"  ✅ Read successfully: +{insertions} lines")
                        else:
                            print(f"  ⚠️  File is EMPTY")
                            diff_text = ""
                            insertions = 0
                            deletions = 0
                    else:
                        print(f"  ⚠️  File NOT FOUND, trying diff...")
                        # 파일이 없으면 diff에서 가져오기 시도
                        diff_text = self._get_diff_text(diff_item)
                        insertions, deletions = self._count_changes(diff_text)
                        print(f"  → From diff: +{insertions}/-{deletions} lines")
                except Exception as e:
                    print(f"  ❌ Error reading file: {e}")
                    import traceback
                    traceback.print_exc()
                    diff_text = self._get_diff_text(diff_item)
                    insertions, deletions = self._count_changes(diff_text)
            else:
                # 수정/삭제/이름변경은 diff에서 가져오기
                diff_text = self._get_diff_text(diff_item)
                insertions, deletions = self._count_changes(diff_text)
                print(f"  → From diff: +{insertions}/-{deletions} lines")
            
            return FileChange(
                path=path,
                change_type=change_type,
                insertions=insertions,
                deletions=deletions,
                diff=diff_text
            )
        except Exception as e:
            print(f"❌ Failed to parse: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _get_diff_text(self, diff_item) -> str:
        """Diff 텍스트 추출"""
        try:
            if hasattr(diff_item, 'diff'):
                if callable(diff_item.diff):
                    diff_data = diff_item.diff()
                else:
                    diff_data = diff_item.diff
                
                if hasattr(diff_data, 'decode'):
                    return diff_data.decode('utf-8', errors='ignore')
                elif diff_data:
                    return str(diff_data)
            return ""
        except Exception as e:
            print(f"Debug: Error getting diff text: {e}")
            return ""
    
    def _count_changes(self, diff_text: str) -> tuple:
        """삽입/삭제 라인 수 계산"""
        insertions = 0
        deletions = 0
        
        for line in diff_text.split('\n'):
            if line.startswith('+') and not line.startswith('+++'):
                insertions += 1
            elif line.startswith('-') and not line.startswith('---'):
                deletions += 1
        
        return insertions, deletions
    
    def get_all_changes(self, include_untracked: bool = False) -> GitChanges:
        """모든 변경사항 가져오기"""
        staged = self.get_staged_changes()
        unstaged = self.get_unstaged_changes()
        
        if include_untracked:
            untracked = self.get_untracked_files()
            for file_path in untracked:
                # Untracked 파일을 FileChange로 변환
                try:
                    full_path = Path(self.repo.working_dir) / file_path
                    if full_path.exists():
                        with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                        
                        unstaged.append(FileChange(
                            path=file_path,
                            change_type='A',
                            insertions=len(content.split('\n')),
                            deletions=0,
                            diff=content
                        ))
                except Exception as e:
                    print(f"Warning: Could not read untracked file {file_path}: {e}")
        
        # 통계 계산
        all_files = staged + unstaged
        total_insertions = sum(f.insertions for f in all_files)
        total_deletions = sum(f.deletions for f in all_files)
        
        return GitChanges(
            staged_files=staged,
            unstaged_files=unstaged,
            total_insertions=total_insertions,
            total_deletions=total_deletions,
            total_files=len(all_files)
        )
    
    def stage_files(self, file_paths: List[str]) -> None:
        """파일들을 staging area에 추가"""
        self.repo.index.add(file_paths)
    
    def stage_all(self) -> None:
        """모든 변경사항을 staging"""
        self.repo.git.add(A=True)
    
    def commit(self, message: str) -> git.Commit:
        """커밋 생성"""
        return self.repo.index.commit(message)
    
    def get_recent_commits(self, count: int = 10) -> List[Dict[str, str]]:
        """최근 커밋 목록 가져오기 (참고용)"""
        commits = []
        for commit in self.repo.iter_commits(max_count=count):
            commits.append({
                'sha': commit.hexsha[:7],
                'message': commit.message.strip(),
                'author': commit.author.name,
                'date': commit.committed_datetime.strftime('%Y-%m-%d %H:%M:%S')
            })
        return commits
    
    def has_changes(self) -> bool:
        """변경사항이 있는지 확인"""
        return (
            self.repo.is_dirty() or 
            len(self.repo.untracked_files) > 0 or
            len(self.repo.index.diff("HEAD")) > 0
        )


if __name__ == "__main__":
    # 테스트 코드
    analyzer = GitAnalyzer()
    
    if analyzer.has_changes():
        changes = analyzer.get_all_changes(include_untracked=True)
        
        print(f"📊 Git 변경사항 분석")
        print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"Staged 파일: {len(changes.staged_files)}")
        print(f"Unstaged 파일: {len(changes.unstaged_files)}")
        print(f"총 파일: {changes.total_files}")
        print(f"삽입: +{changes.total_insertions} 줄")
        print(f"삭제: -{changes.total_deletions} 줄")
        print()
        
        if changes.staged_files:
            print("Staged 파일:")
            for f in changes.staged_files:
                print(f"  {f.change_type} {f.path} (+{f.insertions}/-{f.deletions})")
        
        if changes.unstaged_files:
            print("\nUnstaged 파일:")
            for f in changes.unstaged_files:
                print(f"  {f.change_type} {f.path} (+{f.insertions}/-{f.deletions})")
    else:
        print("변경사항이 없습니다.")

