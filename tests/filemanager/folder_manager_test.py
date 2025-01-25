from filemanager.FolderManager import FolderManager
from filemanager.window_file_open import get_folder_path

import time


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


