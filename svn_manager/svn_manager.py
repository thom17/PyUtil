import subprocess
import xml.etree.ElementTree as ET
from typing import Optional
from datetime import datetime

import re

from svn_data import Log, FileDiff
def get_svn_logs(path: str):


    file_path_map = {}

    logs = Log.from_subprocess_by_path(path)

    for idx, log in enumerate(logs):
        print(f'\r({idx} / {len(logs)}) {log.revision}\t', end="")
        fileDiffList = FileDiff.from_subprocess(path, log.revision)
        # print(len(fileDiffList))
    # log_entries = None
    # log_xml = __get_svn_log_xml(project_a_path)
    # if log_xml:
    #     log_entries = parse_svn_log(log_xml)
    #     print(len(log_entries), "개의 로그")
    #
    #     for idx, entry in enumerate(log_entries):
    #         paths = diff_main(project_a_path, entry['revision'])
    #         entry['changed_paths'] = paths
    #
    #         # print(f"{len(paths)} changes")
    return logs, fileDiffList


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



def parse_svn_log(log_xml):
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



if __name__ == "__main__":
    # path = r'D:\dev\AutoPlanning\Pano\pano-task\mod_APImplantSimulation'
    path = r'D:\dev\AutoPlanning\Pano\pano-task\mod_APImplantSimulation\UIDlgImplantLib.cpp'

    result = __get_svn_log_xml(path)
    print(type(result))
    # print(result)

    data = parse_svn_log(result)


    with open('pano-task-modeIp-log.xml', "w", encoding="utf-8") as f:
        f.write(result)


    # result = get_svn_logs(path)
    # print(type(result))
    # print(result)