from dataclasses import dataclass, field
from typing import List, Union, Dict
from datetime import datetime

from enum import Enum

import subprocess
import xml.etree.ElementTree as ET
import re



class DiffActionType(str, Enum):
    Add = "Added"
    Del = "Deleted"
    Mod = "Modified"
    rep = "Replaced"

    @staticmethod
    def map_code_to_action(action: str) -> 'DiffActionType':
        action = action.upper()
        if action in ['A', 'ADD', 'ADDED']:
            return DiffActionType.Add
        elif action in ['D', 'DEL', 'DELETE', 'DELETED']:
            return DiffActionType.Del
        elif action in ['M', 'MOD', 'MODIFY', 'MODIFIED']:
            return DiffActionType.Mod
        elif action in ['R', 'REP', 'REPLACE', 'REPLACED']:
            return DiffActionType.rep
        else:
            raise ValueError(f"Unrecognized action code: {action}")

@dataclass
class Log:
    revision: str
    author: str
    date: datetime
    msg: str


    @staticmethod
    def from_subprocess_by_path(path: str)-> List["Log"]:
        '''
        os 측에서 직접 실행하여 로그를 생성.
        :param path: 경로
        :return:
        '''
        try:
            result = subprocess.run(['svn', 'log', path, '--xml'], capture_output=True, check=True)
            return Log.from_xml(result.stdout.decode('utf-8'))
        except subprocess.CalledProcessError as e:
            print(f"Error fetching SVN log: {e}")
            return None



    @staticmethod
    def from_xml(context: str) -> List["Log"]:
        """
        XML 문자열을 받아 Log 객체의 리스트를 생성합니다.

        Args:
            context (str): XML 형식의 로그 데이터 문자열

        Returns:
            List[Log]: 파싱된 Log 객체 리스트
        """
        root = ET.fromstring(context)
        log_entries = []

        for logentry in root.findall('logentry'):
            entry = Log(
                revision=logentry.attrib['revision'],
                author=logentry.find('author').text,
                date=datetime.strptime(logentry.find('date').text, '%Y-%m-%dT%H:%M:%S.%fZ'),
                msg=logentry.find('msg').text.strip() if logentry.find('msg') is not None and logentry.find(
                    'msg').text is not None else ''
            )
            log_entries.append(entry)

        return log_entries


@dataclass
class FileDiff:
    revision: str
    filepath: str
    action: DiffActionType

    @staticmethod
    def __subprocess(path: str, revision: Union[str, int]):
        try:
            result = subprocess.run(['svn', 'diff', '--summarize', '-c', str(revision), path], capture_output=True,
                                    text=True, check=True)
            return result.stdout
        except subprocess.CalledProcessError as e:
            print(f"Error fetching SVN diff for revision {revision}: {e}")
            return None

    @staticmethod
    def __parse_subprocess(diff_output: str, revision_number: Union[str, int]) -> List[Dict[str, str]]:
        changed_files = []
        diff_lines = diff_output.splitlines()

        for line in diff_lines:
            match = re.match(r'^[A-Z]\s+(.*)', line)
            if match:
                action = line[0]
                action = DiffActionType.map_code_to_action(action=action)
                file_path = match.group(1)


                changed_files.append( FileDiff(revision=revision_number, action=action, filepath=file_path))


        return changed_files

    @staticmethod
    def from_subprocess(path: str, revision: Union[str, int]) -> List['FileDiff']:
        revision_number = revision  # 원하는 리비전 번호로 변경

        diff_output = FileDiff.__subprocess(path, revision_number)
        if diff_output:
            changed_files = FileDiff.__parse_subprocess(diff_output, revision_number)
            # print(f"Changed files in revision {revision_number}:")
            # for changed_file in changed_files:
            #     action = changed_file['action']
            #     action_desc = ''
            #     if action == 'A':
            #         action_desc = 'Added'
            #     elif action == 'D':
            #         action_desc = 'Deleted'
            #     elif action == 'M':
            #         action_desc = 'Modified'
            #     elif action == 'R':
            #         action_desc = 'Replaced'
            #     print(f"{action_desc}: {changed_file['path']}")
            #
            return changed_files
        else:
            return []


@dataclass
class BlockChanges:
    revision: str
    filepath: str

    old_end: str
    old_start: str

    new_end: str
    new_start: str

    old_block: str
    new_block: str



@dataclass
class LineChanges:
    revision: str
    filepath: str

    line_num: int
    line_str: str

    action: DiffActionType



if __name__ == "__main__":

    #xml 택스트 읽기
    # path = 'pano-task-modeIp-log.xml'
    # with open(path, 'r', encoding="utf-8") as f:
    #     logs=Log.from_xml(f.read())


    #subprocess로 생성하기
    path = r'D:\dev\AutoPlanning\Pano\pano-task\mod_APImplantSimulation\UIDlgImplantLib.cpp'
    logs = Log.from_subprocess_by_path(path)


    print(len(logs), " logs")
    for idx, log  in enumerate(logs):
        if idx %5 == 0:
            print(log)
