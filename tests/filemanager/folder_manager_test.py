import os.path

from filemanager.FolderManager import FolderManager
from filemanager.window_file_open import get_folder_path

import time

from script.fixture_lib.diolib import target_path


def test_folder_with_window_file_open():
    start_time = time.time()
    folder_path = get_folder_path(title='폴더 선택 (test_folder_with_window_file_open)')
    start_time = time.time()
    folder_manager = FolderManager(data=folder_path)
    end_time = time.time()
    print(f"폴더 선택 및 폴더 매니저 생성 소요 시간: {end_time - start_time}초")
    file_size = len(folder_manager.get_file_list())
    dir_size = len(folder_manager.get_dir_list())
    print(f"파일 개수: {file_size}, 디렉토리 개수: {dir_size}")
    total_size = file_size + dir_size
    print(f"총 크기: {total_size} 개수 별 시간 : {(end_time - start_time) * 1000 / file_size:.2f} 밀리초")

import shutil

def copy_file_with_dirs(org_path, target_path):
    os.makedirs(os.path.dirname(target_path), exist_ok=True)
    shutil.copy2(org_path, target_path)

def test_copy_jpg_png():
    source_path = get_folder_path(title='소스 선택')
    folder_manager = FolderManager(data=source_path, skip_dir=['.vs', '.git', '.svn', 'x64', '.dll', '.lib', '.bin', '.obj', '.pdb', '.log', '.db'])
    ext_map = folder_manager.get_type_map()

    target_dir = get_folder_path(title='타겟 선택')


    for path in ext_map['.jpg'] + ext_map['.png']:
        org_path = os.path.join(source_path, path)
        org_path = os.path.normpath(org_path)

        target_path = os.path.join(target_dir, path)
        target_path = os.path.normpath(target_path)

        os.makedirs(os.path.dirname(target_path), exist_ok=True)
        shutil.copy2(org_path, target_path)


test_copy_jpg_png()
