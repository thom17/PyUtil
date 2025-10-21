from dataclasses import dataclass, asdict
from typing import List, Union, Dict, Optional
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

    def __str__(self):
        return self.value

@dataclass
class Log:
    revision: str
    author: str
    date: datetime
    msg: str

    @staticmethod
    def from_subprocess_by_path_with_range(path: str, start_revision: Union[int, str], end_revision: Optional[Union[int, str]] = 'HEAD') -> List["Log"]:
        '''
        os 측에서 직접 실행하여 로그를 생성.
        :param path: 경로
        :param start_revision: 검색을 시작할 리비전 번호 (기본값: None)
        :return: Log 리스트
        '''
        try:
            # 기본 명령어
            command = ['svn', 'log', '-r', f"{start_revision}:{end_revision}", path, '--xml']
# 명령 실행
            result = subprocess.run(command, capture_output=True, check=True)
            return Log.from_xml(result.stdout.decode('utf-8'))
        except subprocess.CalledProcessError as e:
            print(f"Error fetching SVN log: {e}")
            return []
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
    '''
    rv_path  = rv + '#' + repo_path
    '''
    rv_path: str
    revision: str
    file_path: str
    repo_path: str
    name: str
    action: DiffActionType

    def to_dict(self) -> Dict:
        # 기본적으로 dataclass의 asdict 사용하되, action은 문자열로 변환
        data = asdict(self)
        data['action'] = str(self.action.value)  # action Enum을 문자열로 변환
        return data

@dataclass
class BlockChanges:
    revision: str
    file_path: str

    old_end: str
    old_start: str

    new_end: str
    new_start: str

    old_block: str
    new_block: str



@dataclass
class LineChanges:
    revision: str
    file_path: str

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
