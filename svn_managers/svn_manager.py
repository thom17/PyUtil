import os.path

import svn_managers.svn_data_factory as svnFactory
from typing import Dict, Tuple, List, Union
import subprocess
import xml.etree.ElementTree as ET
from typing import Optional, Any
from datetime import datetime

import re
import svn_managers.svn_subprocess as SVNSubprocess
from svn_managers.svn_data import Log, FileDiff
# from svn_data import Log, FileDiff

from functools import singledispatch #오버로딩 처리

def get_diif_map(path: str, revision) -> Dict[FileDiff, List[Dict[str, Any]]]:
    result = {}
    diff_list = svnFactory.make_fileDiff(path, revision)
    for file_diff in diff_list:
        diff_dict = {}
        diff_dict['file_diff'] = file_diff
        diff_dict['block'] = make_block_changes(file_diff)
        diff_dict['line'] = make_line_changes(file_diff)
        result[file_diff.file_path] = diff_dict
    return result

FilePath = str
Revision = Union[str, int]
@singledispatch
def make_block_changes(arg: Union[FileDiff, Tuple[FilePath, Revision]]):
    raise NotImplementedError("Unsupported argument type")

@make_block_changes.register
def _(file_diff: FileDiff):
    return svnFactory.make_block_changes(file_diff=file_diff)

@make_block_changes.register
def _(file_path: FilePath, revision: Revision):
    diff_list = svnFactory.make_fileDiff(file_path, revision)
    assert len(diff_list) == 1, f'{file_path}'
    file_diff = diff_list[0]
    return make_block_changes(file_diff)

@singledispatch
def make_line_changes(arg):
    raise NotImplementedError("Unsupported argument type")

@make_line_changes.register
def _(file_diff: FileDiff):
    return svnFactory.make_line_changes(file_diff=file_diff)

@make_line_changes.register
def _(file_path: str, revision: str):
    diff_list = svnFactory.make_fileDiff(file_path, revision)
    assert len(diff_list) == 1, f'{file_path}'
    file_diff = diff_list[0]
    return make_line_changes(file_diff)

def do_update(path: str, revision: Union[int, str] = 'HEAD') -> Dict[str, List[str]]:
    return SVNSubprocess.do_update(path, revision)

def get_modified_files(path: str, status_filters : List[str] = ["M"]) -> List[str]:
    '''
    수정된 파일 목록을 반환한다.
    '''
    return SVNSubprocess.get_modified_files(path, status_filters)

def get_list(dir_path: str, visit_dir = True) -> List[str]:
    '''
    디렉토리 내의 모든 파일 목록을 반환한다. (폴더 내부 기본적으로 포함)
    '''
    assert os.path.isdir(dir_path), f'{dir_path} is not a directory'

    files =[dir_path + os.sep + path for path in SVNSubprocess.get_list(dir_path)]
    if not visit_dir:
        files = [f for f in files if not os.path.isdir(f)]

    return files



def get_before_change_rv(path: str, revision: Union[int, str]) -> Optional[Union[int, str]]:
    path = get_repo_url(path)
    logs = Log.from_subprocess_by_path(path)
    for log in logs: #내림차순으로 정렬되있음
        # 추후에 문제될수 있음. to do : 리비전 비교 처리.
        rv_num = int(log.revision)
        revision = int(revision)
        if rv_num < revision:
            return log.revision
    return None

def do_revert(path: str) ->List[str]:
    return SVNSubprocess.do_revert(path)

def get_svn_range_log_dif(path: str, start_revision: Union[int, str], end_revision: Optional[Union[int, str]] = 'HEAD') -> Dict[str, Tuple[Log, List[FileDiff]]]:
    '''
    log -> List[fileDiff]를 구하는 함수로
    전반적인 변화, 건드린 파일을 찾는대 사용
    :param path:
    :return: [리비전] = (Log, [FileDiff])
    '''
    logs_map = {}
    logs = Log.from_subprocess_by_path_with_range(path, start_revision=start_revision, end_revision=end_revision)
    file_dif_size = 0

    for idx, log in enumerate(logs):
        print(f'\r({idx} / {len(logs)}) {log.revision}\t', end="")
        fileDiffList = svnFactory.make_fileDiff(path, log.revision)
        logs_map[log.revision] = (log, fileDiffList)
        file_dif_size += len(fileDiffList)
    print(f'{len(logs)}) done. {file_dif_size} change file times \t')

    return logs_map


def get_svn_logs(path: str) -> Dict[str, Tuple[Log, List[FileDiff]]]:
    '''
    log -> List[fileDiff]를 구하는 함수로
    전반적인 변화, 건드린 파일을 찾는대 사용
    :param path:
    :return: [리비전] = (Log, [FileDiff])
    '''
    logs_map = {}
    logs = Log.from_subprocess_by_path(path)
    file_dif_size = 0

    for idx, log in enumerate(logs):
        print(f'\r({idx} / {len(logs)}) {log.revision}\t', end="")
        fileDiffList = svnFactory.make_fileDiff(path, log.revision)
        logs_map[log.revision] = (log, fileDiffList)
        file_dif_size += len(fileDiffList)
    print(f'{len(logs)}) done. {file_dif_size} change file times \t')

    return logs_map
    # return logs, fileDiffList


def get_recent_logs(path: str, count=50) -> Dict[str, Tuple[Log, List[FileDiff]]]:
    '''
    get_svn_logs 에서 검색하는 버전 수를 제한한 것.
    '''
    # Get the HEAD revision
    cur_revision = get_current_revision(path)
    if cur_revision is None:
        return {}

    # Get all revisions for the path
    # all_revisions = get_repo_revisions(path)
    logs = Log.from_subprocess_by_path_with_range(path=path, start_revision='0', end_revision=cur_revision)
    all_revisions = [log.revision for log in logs]

    # Take only the most recent 'count' revisions (오름 차순 : 1, 2, 3, ...)
    recent_revisions = all_revisions[-min(count, len(all_revisions)):]

    if not recent_revisions:
        return {}

    # Get the oldest revision from our limited set
    start_revision = recent_revisions[0]

    # Get logs for the specified range
    return get_svn_range_log_dif(path, start_revision, cur_revision)

def get_repo_url(path: str) -> str:
    return SVNSubprocess.get_repo_url(path)

def get_repo_revisions(path: str) -> List[str]:
    '''
    Repo(최신)의 경로에 대한 모든 리비전 번호.
    '''

    path = SVNSubprocess.get_repo_url(path)
    logs = Log.from_subprocess_by_path(path)
    return [log.revision for log in logs]



def get_file_at_revision(file_path: str, revision: int) -> str:
    return SVNSubprocess.get_file_at_revision(file_path, revision=revision)

def get_line_changes_log_map(file_path: str):
    logs_map = {}
    logs = Log.from_subprocess_by_path(file_path)
    line_change_size = 0
    for idx, log in enumerate(logs):
        print(f'\r({idx} / {len(logs)}) {log.revision}\t', end="")
        fileDiffList = svnFactory.make_fileDiff(file_path, log.revision)
        file_diff = fileDiffList[0]
        line_changes = svnFactory.make_line_changes(file_diff)
        logs_map[log.revision] = line_changes

        line_change_size += len(line_changes)
    print(f'{len(logs)}) done. {line_change_size} change file times \t')
    return logs_map



# logs, fileDiffList = get_svn_logs(r'D:\dev\AutoPlanning\trunk\AP_Lib_UI_Task 4289\AppFrame')

# path = r'D:\dev\AutoPlanning\Pano\pano-task\mod_APImplantSimulation'
# log, diff =  get_svn_logs(path)
# print()

def __get_svn_log_xml(path : str) -> Optional[str]:
    '''
    특정 경로에 대한 로그를 xml 형식으로 만들어 반환.
    (변경 파일 및 내용에 해당하는 정보는 없음)
    :param path: 로그를 볼 경로
    :return: str (xml)
    '''
    try:
        result = subprocess.run(['svn', 'log', path, '--xml'], capture_output=True, check=True)
        return result.stdout.decode('utf-8')
    except subprocess.CalledProcessError as e:
        print(f"Error fetching SVN log: {e}")
        return None



def __xml_parse_svn_log(log_xml):
    root = ET.fromstring(log_xml)
    log_entries = []

    for logentry in root.findall('logentry'):
        entry = {
            'revision': logentry.attrib['revision'],
            'author': logentry.find('author').text,
            'date': datetime.strptime(logentry.find('date').text, '%Y-%m-%dT%H:%M:%S.%fZ'),
            'message': logentry.find('msg').text.strip() if logentry.find('msg') is not None and logentry.find(
                'msg').text is not None else '',
            'changed_paths': []
        }

        paths = logentry.find('paths')
        if paths is not None:
            for path in paths.findall('path'):
                entry['changed_paths'].append({
                    'action': path.attrib['action'],
                    'path': path.text
                })

        log_entries.append(entry)

    return log_entries


def is_pulled_path(path: str):
    return get_current_revision(path) == get_repo_url(path)

def get_current_revision(path: str):
    """
    Get the current revision of the specified path.
    """
    command = ["svn", "info", path]
    try:
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        for line in result.stdout.splitlines():
            if line.startswith("Revision:") or line.startswith("리비전:"):
                return int(line.split(":")[1].strip())
    except subprocess.CalledProcessError as e:
        print(f"Error retrieving current revision: {e.stderr}")
        return None
def get_head_revision_map(path: str) -> Dict[Revision, list[FilePath]]:
    '''
    경로 내의 모든 파일에 대하여 각각의 최신 리비전으로 mapping된 딕셔너리 반환.
    '''

    head_revision = get_head_revision(path)
    logs = Log.from_subprocess_by_path(path)
    revision_map: Dict[Revision, list[FilePath]] = {}

    for log in logs:
        for file_diff in svnFactory.make_fileDiff(path, log.revision):
            if log.revision == head_revision:
                revision_map.setdefault(log.revision, []).append(file_diff.file_path)
    return revision_map



def get_head_revision(repo_url: str):
    """
    Get the head revision of the specified SVN repository.
    """
    repo_url = get_repo_url(repo_url)

    command = ["svn", "info", repo_url]
    try:
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        for line in result.stdout.splitlines():
            if line.startswith("Revision:") or line.startswith("리비전:"):
                return int(line.split(":")[1].strip())
    except subprocess.CalledProcessError as e:
        print(f"Error retrieving head revision: {e.stderr}")
        return None



if __name__ == "__main__":
    path = r'D:\dev\AutoPlanning\Pano\pano-task\mod_APImplantSimulation'
    # path = r'D:\dev\AutoPlanning\Pano\pano-task\mod_APImplantSimulation\UIDlgImplantLib.cpp'

    head_map = get_head_revision_map(path)
    print(f'head map size : {len(head_map)}')
    for revision, file_paths in head_map.items():
        print(f'Revision: {revision}, Files: {len(file_paths)}')

    # result = __get_svn_log_xml(path)
    # print(type(result))
    # # print(result)
    #
    # data = __xml_parse_svn_log(result)
    #
    #
    # with open('pano-task-modeIp-log.xml', "w", encoding="utf-8") as f:
    #     f.write(result)


    # result = get_svn_logs(path)
    # print(type(result))
    # print(result)