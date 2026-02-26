from svn_managers.svn_diff_data import FileChange, Hunk, Change

import subprocess
import re

from typing import List, Optional, Union

class SvnDiffParseDatas:
    def __init__(self, diff_output: str, rv: str):
        '''
        changes : 모든 변경 사항 (파일 별 정렬)
        :param diff_output:
        '''
        self.rv = rv
        self.diff_output = diff_output
        self.changes: List[FileChange] = []
        self.__parse()


    @staticmethod
    def GetDiff(file_path: str, revision_number: Union[int, str]) -> 'SvnDiffParseDatas':
        '''
        특정 리비전의 SvnDiffParser 생성
        :param file_path:
        :param revision_number:
        :return:
        '''
        # SVN diff 명령어 실행
        before_rv = int(revision_number) - 1
        command = ["svn", "diff", "-r", f"{before_rv}:{revision_number}", file_path]
        # print(" ".join(command))

        try:
            result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

            if result.returncode == 0:
                # diff 결과를 dict로 파싱
                return SvnDiffParseDatas(result.stdout, revision_number)
            else:
                return {"error": result.stderr}
        except Exception as e:
            return {"exception": str(e)}

    @staticmethod
    def GetDiffLocal(file_path: str) -> 'SvnDiffParseDatas':
        '''
        특정 리비전의 SvnDiffParser 생성
        :param file_path:
        :param revision_number:
        :return:
        '''
        # SVN diff 명령어 실행
        before_rv = int(revision_number) - 1
        command = ["svn", "diff", file_path]
        # print(" ".join(command))

        try:
            result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

            if result.returncode == 0:
                # diff 결과를 dict로 파싱
                return SvnDiffParseDatas(result.stdout, revision_number)
            else:
                return {"error": result.stderr}
        except Exception as e:
            return {"exception": str(e)}

    def __parse(self):
        current_file: Optional[FileChange] = None
        current_hunk: Optional[Hunk] = None
        
        for line in self.diff_output.splitlines():
            # 파일 경로 파악
            if line.startswith("Index:"):
                file_path = line.split(" ")[1]
                current_file = FileChange(file_path, self.rv)
                self.changes.append(current_file)

            # 변경된 줄 정보 파악 (ex: @@ -1,4 +1,4 @@)
            elif line.startswith("@@"):
                hunk_info = re.search(r"@@ -(\d+),?(\d+)? \+(\d+),?(\d+)? @@", line)
                if hunk_info:
                    old_start = int(hunk_info.group(1))
                    new_start = int(hunk_info.group(3))
                    current_hunk = Hunk(old_start, new_start)
                    if current_file:
                        current_file.add_hunk(current_hunk)

            # 제거된 줄 파악
            elif line.startswith("-") and not line.startswith("---"):
                if current_hunk:
                    current_hunk.removed.append(Change(current_hunk.old_line, line[1:].strip()))
                    current_hunk.old_line += 1

            # 추가된 줄 파악
            elif line.startswith("+") and not line.startswith("+++"):
                if current_hunk:
                    current_hunk.added.append(Change(current_hunk.new_line, line[1:].strip()))
                    current_hunk.new_line += 1

            # 변경되지 않은 줄은 줄 번호만 증가
            elif not line.startswith("+") and not line.startswith("-") and current_hunk:
                current_hunk.old_line += 1
                current_hunk.new_line += 1

if __name__ == "__main__":

    project_folder = r'D:/dev/AutoPlanning/trunk/AP_trunk_pure/'
    revision_number = 7250

    diff_dict = SvnDiffParseDatas.GetDiff(project_folder, revision_number)
    path = r'D:/dev/AutoPlanning/trunk/AP_trunk_pure/AppFrame/NerveData.h'
    for file_change in diff_dict.changes:
        print(file_change.file_path)

        # print(type(file_change))
        # if file_change.file_path == path:
        #     for hunk in file_change.hunks:
        #         print(f'{hunk.old_line}/{hunk.new_line} -> add/remove ({len(hunk.added)}/{len(hunk.removed)})')
        #         for change_line in hunk.added:
        #             print(f'+{change_line.line_number}\t{change_line.content}')
        #         for change_line in hunk.removed:
        #             print(f'-{change_line.line_number}\t{change_line.content}')

    # print(diff_dict.diff_output)


