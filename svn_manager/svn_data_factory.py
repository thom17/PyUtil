from svn_manager.svn_data import Log, FileDiff, BlockChanges, LineChanges, DiffActionType
from svn_manager.svn_dif_Parser import SvnDiffParseDatas

from typing import List, Union


def make_logs(path: str) -> List[Log]:
    return Log.from_subprocess_by_path(path)

def make_fileDiff(path: str, revision: Union[str, int]) -> List['FileDiff']:
    return FileDiff.from_subprocess(path=path, revision=revision)

def make_block_changes(file_diff: FileDiff) -> List[BlockChanges]:
    block_change_list = []
    parse_datas = SvnDiffParseDatas.GetDiff(file_path=file_diff.filepath, revision_number=file_diff.revision)
    for file_change in parse_datas.changes:
        for hunk, block_pair in file_change.get_hunks_map().items():
            block_change_list.append(
                BlockChanges(
                    revision=file_diff.revision,
                    filepath=file_diff.filepath,
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
    parse_datas = SvnDiffParseDatas.GetDiff(file_path=file_diff.filepath, revision_number=file_diff.revision)
    for file_change in parse_datas.changes:
        line_change_pair = file_change.get_all_change_pair()
        for change_line in line_change_pair[0]:
            line_change_list.append(
                LineChanges(
                    filepath=file_diff.filepath, revision=file_diff.revision,
                    line_str=change_line.content, line_num=change_line.line_number, action=DiffActionType.Del)
            )

        for change_line in line_change_pair[1]:
            line_change_list.append(
                LineChanges(
                    filepath=file_diff.filepath, revision=file_diff.revision,
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
