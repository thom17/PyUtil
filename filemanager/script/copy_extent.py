'''
특정 확장자를 가진 파일을 복사하는 스크립트
'''
import os
import shutil
import sys

args = sys.argv
this_file_path = args[0]
sys.path.append(os.path.dirname(this_file_path+'../../'))


from filemanager.FolderManager import FolderManager, show_checklist_popup
from filemanager.window_file_open import get_folder_path
from qt_util.simple_popup import show_checklist_popup

#step1. 파라미터 설정
def set_param():
    folder_manager = None
    if len(args) < 4:
        source_folder = get_folder_path(title='복사할 원본 소스 폴더 선택')
        target_folder = get_folder_path(title='생성(저장)할 폴더 선택')

        folder_manager = FolderManager(data=source_folder)
        type_map = folder_manager.get_type_map()
        copy_types = show_checklist_popup(type_map)
    else:
        source_folder = args[1]
        target_folder = args[2]
        copy_types = args[3]
    if folder_manager is None:
        folder_manager = FolderManager(data=source_folder)

    return source_folder, target_folder, copy_types, folder_manager
source_folder, target_folder, copy_types, folder_manager = set_param()

#step2. 파일 복사
def copy_file(source_folder, target_folder, copy_types, folder_manager: FolderManager):
    type_map = folder_manager.get_type_map()
    if copy_types == '*':
        copy_types = type_map.keys()
    copy_list = []
    for type_name in copy_types:
        copy_list.extend(type_map[type_name])

    for copy_file in copy_list:
        soure_path = source_folder + os.sep + copy_file
        target_path = target_folder + os.sep + copy_file
        os.makedirs(os.path.dirname(target_path), exist_ok=True)
        shutil.copy2(soure_path, target_path)
        print(f"복사 완료: {copy_file}")
        
copy_file(source_folder, target_folder, copy_types, folder_manager)


