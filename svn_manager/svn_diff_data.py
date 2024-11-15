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


class FileChange:
    def __init__(self, file_path: str, rv: str):
        self.rv = rv
        self.file_path = file_path
        self.hunks: List[Hunk] = []


    def read_pair(self) ->Tuple[str, str]:
        """
        Get the content of a file at a specific SVN revision.

        Args:
            file_path (str): Path to the file in the SVN repository.
            revision_number (int): The revision number to fetch.

        Returns:
            str: The content of the file at the specified revision.
        """
        try:
            before_rv = int(self.rv) - 1
            command = ["svn", "cat", self.file_path, "-r", str(before_rv)]

            result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
            before_code = result.stdout  # The file content as a string

            command = ["svn", "cat", self.file_path, "-r", str(self.rv)]
            result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
            after_code = result.stdout  # The file content as a string

            return (before_code, after_code)

        except subprocess.CalledProcessError as e:
            print(f"Error fetching file content for revision {before_rv}: {e.stderr}")
            return (before_rv, e.stderr)

    def get_hunks_map(self)->Dict[str, str]:
        '''
        hunk를 간단하게 block 2 block으로 변경한다.
        :return: Dict[beforeBlock: str, afterBlock: str]
        '''

        before_source_code, after_source_code = self.read_pair()
        before_source_code = before_source_code.splitlines()
        after_source_code = after_source_code.splitlines()

        blocks_map = {}

        for hunk in self.hunks:
            before_block = before_source_code[hunk.old_start:hunk.old_line]
            after_block = after_source_code[hunk.new_start:hunk.new_line]

            before_block = '\n'.join(before_block)
            after_block = '\n'.join(after_block)

            range_str = f'{hunk.old_start}:{hunk.old_line}-{hunk.new_start}:{hunk.new_line}'

            blocks_map[range_str] = (before_block, after_block)

        return blocks_map

    def get_all_change_pair(self) -> Tuple[List[Change], List[Change]]:
        '''
        해당 파일의 변경 사항을 라인별로 모두 반환
        :return: del_changes, add_changes
        '''
        del_list: List[Change] = []
        add_list: List[Change] = []

        for hunk in self.hunks:
            del_list.extend(hunk.removed)
            add_list.extend(hunk.added)
        return del_list, add_list


    def add_hunk(self, hunk: Hunk):
        self.hunks.append(hunk)

    def __repr__(self):
        return f"FileChange(file_path={self.file_path}, hunks={self.hunks})"