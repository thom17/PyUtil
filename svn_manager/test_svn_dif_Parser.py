from unittest import TestCase
from svn_dif_Parser import SvnDiffParseDatas

class TestSvnDiffParseDatas(TestCase):
    def test_change_line_check(self):
        path = r'D:/dev/AutoPlanning/trunk/AP_trunk_pure/mod_APReady/ActuatorCSNerve.cpp'
        revision_number = 7250

        diff_dict = SvnDiffParseDatas.GetDiff(path, revision_number)
        for file_change in diff_dict.changes:
            #먼저 파일 읽고 리스트 화 (라인번호를 맞추기위해 0번 인덱스 추가)
            before_file, after_file = file_change.read_pair()
            before_list = [''] + before_file.splitlines()
            after_list = [''] + after_file.splitlines()

            #라인별 파일 정보
            del_changes, add_changes = file_change.get_all_change_pair()

            #먼저 삭제의 경우. 이전 소스에서 해당하는 라인을 전체적으로 제거
            del_line_nums = [change.line_number for change in del_changes]
            line = 1
            while line<len(before_list):
                if not line in del_line_nums:
                    before_list[0] += before_list[line] +'\n'
                line += 1

            #추가의 경우 현제 소스에서 추가된 라인을 삭제 한다면 이전 소스에서 삭제 한 것과 같아야 함
            added_line_nums = [change.line_number for change in add_changes]
            line = 1
            while line < len(after_list):
                if not line in added_line_nums:
                    after_list[0] += after_list[line] +'\n'
                line += 1

            with open('../filemanager/before.cpp', 'w') as f:
                f.write(before_list[0])
            with open('../filemanager/after.cpp', 'w') as f:
                f.write(after_list[0])

            assert before_list[0] == after_list[0]
            print('ok')







    def test_get_diff(self):
        # project_folder = r'D:/dev/AutoPlanning/trunk/AP_trunk_pure/AppFrame/NerveData.h'
        project_folder = r'D:/dev/AutoPlanning/trunk/AP_trunk_pure/mod_APReady/ActuatorCSNerve.cpp'
        revision_number = 7250

        diff_dict = SvnDiffParseDatas.GetDiff(project_folder, revision_number)
        for file_change in diff_dict.changes:
            print('---', file_change.file_path, '---', 'hunk ', len(file_change.hunks))
            # read_pair = file_change.read_pair()

            block_map = file_change.get_hunks_map()
            pairs = file_change.get_all_change_pair()

            for key, data in block_map.items():
                print(key, " : ")
                print('before : ')
                print(data[0])
                print('after : ')
                print(data[1])

            for hunk in file_change.hunks:
                hunk.print_info()

            # print(type(file_change))
            # if file_change.file_path == path:
            #     for hunk in file_change.hunks:
            #         print(f'{hunk.old_line}/{hunk.new_line} -> add/remove ({len(hunk.added)}/{len(hunk.removed)})')
            #         for change_line in hunk.added:
            #             print(f'+{change_line.line_number}\t{change_line.content}')
            #         for change_line in hunk.removed:
            #             print(f'-{change_line.line_number}\t{change_line.content}')

        # print(diff_dict.diff_output)

        # self.fail()
