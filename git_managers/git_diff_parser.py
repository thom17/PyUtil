from git_managers.git_diff_data import GitFileChange, Hunk, Change

import subprocess
import re

from typing import List, Optional


class GitDiffParser:
    def __init__(self, diff_output: str, commit_hash: str):
        """
        diff 출력을 파싱하여 changes 생성.

        Args:
            diff_output (str): git diff 명령 출력 문자열
            commit_hash (str): 대상 커밋 해시
        """
        self.commit_hash = commit_hash
        self.diff_output = diff_output
        self.changes: List[GitFileChange] = []
        self.__parse()

    @staticmethod
    def GetDiff(repo_path: str, commit_hash: str) -> 'GitDiffParser':
        """
        특정 커밋의 diff를 가져와서 GitDiffParser 인스턴스 생성.
        git diff <commit>~1 <commit> 명령 사용.

        Args:
            repo_path (str): 저장소 경로
            commit_hash (str): 커밋 해시

        Returns:
            GitDiffParser: 파싱된 diff 인스턴스
        """
        command = ["git", "-C", repo_path, "diff", f"{commit_hash}~1", commit_hash]
        try:
            result = subprocess.run(
                command,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                encoding='utf-8', errors='replace'
            )
            if result.returncode == 0:
                return GitDiffParser(result.stdout, commit_hash)
            else:
                print(f"git diff error: {result.stderr}")
                return GitDiffParser('', commit_hash)
        except Exception as e:
            print(f"Exception running git diff: {e}")
            return GitDiffParser('', commit_hash)

    @staticmethod
    def GetDiffRange(repo_path: str, from_hash: str, to_hash: str) -> 'GitDiffParser':
        """
        두 커밋 간의 diff를 가져와서 GitDiffParser 인스턴스 생성.

        Args:
            repo_path (str): 저장소 경로
            from_hash (str): 시작 커밋 해시
            to_hash (str): 끝 커밋 해시

        Returns:
            GitDiffParser: 파싱된 diff 인스턴스
        """
        command = ["git", "-C", repo_path, "diff", from_hash, to_hash]
        try:
            result = subprocess.run(
                command,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                encoding='utf-8', errors='replace'
            )
            if result.returncode == 0:
                return GitDiffParser(result.stdout, to_hash)
            else:
                print(f"git diff error: {result.stderr}")
                return GitDiffParser('', to_hash)
        except Exception as e:
            print(f"Exception running git diff: {e}")
            return GitDiffParser('', to_hash)

    def __parse(self):
        """
        unified diff 포맷 파싱.
        Git diff 헤더, 파일 경로, hunk 헤더, 변경 라인을 처리.
        """
        current_file: Optional[GitFileChange] = None
        current_hunk: Optional[Hunk] = None

        for line in self.diff_output.splitlines():
            # Git diff 헤더: diff --git a/path b/path
            if line.startswith("diff --git "):
                current_hunk = None
                current_file = None

            # 파일 경로 추출: --- a/path (이전 파일)
            elif line.startswith("--- a/"):
                file_path = line[6:]
                current_file = GitFileChange(file_path, self.commit_hash)
                self.changes.append(current_file)
                current_hunk = None

            # 새 파일 생성의 경우 +++ b/path (이전 없음)
            elif line.startswith("+++ b/") and current_file is None:
                file_path = line[6:]
                current_file = GitFileChange(file_path, self.commit_hash)
                self.changes.append(current_file)
                current_hunk = None

            # hunk 헤더: @@ -old_start,old_count +new_start,new_count @@
            elif line.startswith("@@"):
                hunk_info = re.search(r"@@ -(\d+),?(\d+)? \+(\d+),?(\d+)? @@", line)
                if hunk_info and current_file:
                    old_start = int(hunk_info.group(1))
                    new_start = int(hunk_info.group(3))
                    current_hunk = Hunk(old_start, new_start)
                    current_file.add_hunk(current_hunk)

            # 제거된 줄
            elif line.startswith("-") and not line.startswith("---"):
                if current_hunk:
                    current_hunk.removed.append(Change(current_hunk.old_line, line[1:]))
                    current_hunk.old_line += 1

            # 추가된 줄
            elif line.startswith("+") and not line.startswith("+++"):
                if current_hunk:
                    current_hunk.added.append(Change(current_hunk.new_line, line[1:]))
                    current_hunk.new_line += 1

            # 변경되지 않은 context 줄
            elif line.startswith(" ") and current_hunk:
                current_hunk.old_line += 1
                current_hunk.new_line += 1
