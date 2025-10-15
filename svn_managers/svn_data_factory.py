from svn_managers.svn_data import Log, FileDiff, BlockChanges, LineChanges, DiffActionType
from svn_managers.svn_dif_Parser import SvnDiffParseDatas
from svn_managers.svn_subprocess import get_repo_url

from typing import List, Union, Dict
import subprocess
import xml.etree.ElementTree as ET
import re



def make_logs(path: str) -> List[Log]:
    return Log.from_subprocess_by_path(path)
    # to do

def make_fileDiff(path: str, revision: Union[str, int]) -> List[FileDiff]:

    repo_url = get_repo_url(file_path=path)
    def __convert_url_path(file_path: str) -> str:
        file_path = file_path.replace(path, repo_url)
        return file_path

    def __subprocess(path: str, revision: Union[str, int]):
        try:
            result = subprocess.run(['svn', 'diff', '--summarize', '-c', str(revision), path], capture_output=True,
                                    text=True, check=True)
            return result.stdout
        except subprocess.CalledProcessError as e:
            print(f"Error fetching SVN diff for revision {revision}: {e}")
            return None

    def __parse_subprocess_diff(diff_output: str, revision_number: Union[str, int]) -> List[Dict[str, str]]:
        changed_files = []
        diff_lines = diff_output.splitlines()

        for line in diff_lines:
            match = re.match(r'^[A-Z]\s+(.*)', line)
            if match:
                action = line[0]
                action = DiffActionType.map_code_to_action(action=action)
                file_path = match.group(1)

                repo_url = __convert_url_path(file_path=file_path)

                rv_path = revision_number + '#' + repo_url


                changed_files.append(
                    FileDiff(revision=revision_number, action=action,
                             file_path=file_path, rv_path=rv_path, repo_path=repo_url))

        return changed_files



    revision_number = str(revision)  # 원하는 리비전 번호로 변경

    diff_output = __subprocess(path, revision_number)
    if diff_output:
        changed_files = __parse_subprocess_diff(diff_output, revision_number)
        return changed_files
    else:
        return []


def make_block_changes(file_diff: FileDiff) -> List[BlockChanges]:
    block_change_list = []
    parse_datas = SvnDiffParseDatas.GetDiff(file_path=file_diff.file_path, revision_number=file_diff.revision)
    for file_change in parse_datas.changes:
        for hunk, block_pair in file_change.get_hunks_map().items():
            block_change_list.append(
                BlockChanges(
                    revision=file_diff.revision,
                    file_path=file_diff.file_path,
                    old_start=hunk.old_start,
                    old_end=hunk.old_line,
                    new_start=hunk.new_start,
                    new_end=hunk.new_line,
                    old_block=block_pair[0],
                    new_block=block_pair[1])
            )

    return block_change_list


def make_line_changes(file_diff: FileDiff) -> List[LineChanges]:
    line_change_list = []
    parse_datas = SvnDiffParseDatas.GetDiff(file_path=file_diff.file_path, revision_number=file_diff.revision)
    for file_change in parse_datas.changes:
        line_change_pair = file_change.get_all_change_pair()
        for change_line in line_change_pair[0]:
            line_change_list.append(
                LineChanges(
                    file_path=file_diff.file_path, revision=file_diff.revision,
                    line_str=change_line.content, line_num=change_line.line_number, action=DiffActionType.Del)
            )

        for change_line in line_change_pair[1]:
            line_change_list.append(
                LineChanges(
                    file_path=file_diff.file_path, revision=file_diff.revision,
                    line_str=change_line.content, line_num=change_line.line_number, action=DiffActionType.Add)
            )

    return line_change_list


# if __name__ == "__main__":
#     path = r'D:/dev/AutoPlanning/trunk/AP_trunk_pure/mod_APReady/ActuatorCSNerve.cpp'
#     revision_number = 7250
#
#     file_diffs =make_fileDiff(path, revision_number)
#     assert len(file_diffs) == 1, '파일을 경로로 태스트 해야함'
#     block_changes = make_block_changes(file_diffs[0])
#
#     for change in block_changes:
#         print(change)
#
#     line_changes = make_line_changes(file_diffs[0])
#     print(len(line_changes))
#     add_line = []
#     del_line = []
#     for change in line_changes:
#         if change.action == DiffActionType.Add:
#             add_line.append(change)
#         else:
#             del_line.append(change)
#     print('del ',len(del_line), ', add ',len(add_line))
