from typing import List, Dict, Tuple
import subprocess


class Change:
    def __init__(self, line_number: int, content: str):
        self.line_number = line_number
        self.content = content

    def __repr__(self):
        return f"{self.line_number}: {self.content}"


class Hunk:
    def __init__(self, old_start: int, new_start: int):
        self.old_start = old_start
        self.new_start = new_start
        self.old_line = old_start
        self.new_line = new_start
        self.added: List[Change] = []
        self.removed: List[Change] = []

    def print_info(self):
        print(f'Hunk {self.old_start}-{self.old_line} {self.new_start}-{self.new_line}')
        print(f'{len(self.added)} added, {len(self.removed)} removed')

        for change in self.added:
            print(f'+{change.line_number}\t{change.content}')

        for change in self.removed:
            print(f'-{change.line_number}\t{change.content}')
        print()

    def __repr__(self):
        return f"Hunk(old_start={self.old_start}, new_start={self.new_start}, added={self.added}, removed={self.removed})"


class GitFileChange:
    def __init__(self, file_path: str, commit_hash: str = ''):
        self.file_path = file_path
        self.commit_hash = commit_hash
        self.hunks: List[Hunk] = []

    def read_pair(self, commit_hash: str = '') -> Tuple[str, str]:
        """
        git show 명령으로 특정 커밋 전후의 파일 내용을 가져온다.

        Args:
            commit_hash (str): 커밋 해시. 비어 있으면 self.commit_hash 사용.

        Returns:
            Tuple[str, str]: (이전 파일 내용, 이후 파일 내용)
        """
        target_hash = commit_hash if commit_hash else self.commit_hash
        try:
            before_ref = f"{target_hash}~1:{self.file_path}"
            command_before = ["git", "show", before_ref]
            result_before = subprocess.run(
                command_before,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                encoding='utf-8', errors='replace'
            )
            before_code = result_before.stdout

            after_ref = f"{target_hash}:{self.file_path}"
            command_after = ["git", "show", after_ref]
            result_after = subprocess.run(
                command_after,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                encoding='utf-8', errors='replace'
            )
            after_code = result_after.stdout

            return (before_code, after_code)

        except Exception as e:
            print(f"Error fetching file content for commit {target_hash}: {e}")
            return ('', '')

    def get_hunks_map(self) -> Dict[Hunk, Tuple[str, str]]:
        """
        hunk를 block 단위(before/after)로 매핑.

        Returns:
            Dict[Hunk, Tuple[str, str]]: hunk -> (before_block, after_block)
        """
        before_source_code, after_source_code = self.read_pair()
        before_lines = before_source_code.splitlines()
        after_lines = after_source_code.splitlines()

        blocks_map = {}

        for hunk in self.hunks:
            before_block = before_lines[hunk.old_start - 1:hunk.old_line - 1]
            after_block = after_lines[hunk.new_start - 1:hunk.new_line - 1]

            before_block = '\n'.join(before_block)
            after_block = '\n'.join(after_block)

            blocks_map[hunk] = (before_block, after_block)

        return blocks_map

    def get_all_change_pair(self) -> Tuple[List[Change], List[Change]]:
        """
        해당 파일의 변경 사항을 라인별로 모두 반환.

        Returns:
            Tuple[List[Change], List[Change]]: (del_changes, add_changes)
        """
        del_list: List[Change] = []
        add_list: List[Change] = []

        for hunk in self.hunks:
            del_list.extend(hunk.removed)
            add_list.extend(hunk.added)

        return del_list, add_list

    def add_hunk(self, hunk: Hunk):
        self.hunks.append(hunk)

    def __repr__(self):
        return f"GitFileChange(file_path={self.file_path}, hunks={self.hunks})"
