import os.path
from typing import List, Dict, Union
import chardet                  #for py 11

from typing import Union, TextIO, Optional
import os
from PyQt5.QtWidgets import QApplication, QDialog, QVBoxLayout, QCheckBox, QPushButton
import sys


def show_checklist_popup(type_map:Dict[str,List[str]]) ->List[str]:
    """
    확장명,

    Returns:
        list: A list of selected types.
    """
    app = QApplication.instance() or QApplication(sys.argv)  # Ensure QApplication exists
    dialog = QDialog()
    dialog.setWindowTitle("Check List")

    layout = QVBoxLayout()
    checkboxes = []

    # Create checkboxes for each key in the type_map
    for key, values in type_map.items():
        checkbox = QCheckBox(f"{key}: {len(values)}")
        layout.addWidget(checkbox)
        checkboxes.append((key, checkbox))

    ok_button = QPushButton("확인")
    layout.addWidget(ok_button)

    def on_ok():
        # Store selected types in the dialog
        dialog.selected_types = [key for key, checkbox in checkboxes if checkbox.isChecked()]
        dialog.accept()

    ok_button.clicked.connect(on_ok)
    dialog.setLayout(layout)
    dialog.exec_()

    # Return the selected types
    return dialog.selected_types


def clean_path(path: str, absolute: bool = True, separator = os.sep) -> str:
    """경로를 깔끔하게 정리하고 구분자를 설정하여 반환합니다.

    Args:
        path (str): 정리할 경로 문자열.
        absolute (bool): True일 경우 절대 경로로 반환, False일 경우 상대 경로로 반환.
        separator (Optional[str]): 경로 구분자. 기본값은 os의 기본 구분자.

    Returns:
        str: 정리된 경로 문자열.
    """

    # 기본 구분자를 운영체제 기본 구분자로 설정
    if separator is None:
        separator = os.sep

    # 경로 정리
    normalized_path = os.path.normpath(path)  # 불필요한 슬래시와 백슬래시를 제거

    # 절대 경로 또는 상대 경로로 반환
    final_path = os.path.abspath(normalized_path) if absolute else normalized_path

    # 사용자 지정 구분자로 경로 구분자 변경
    if separator != os.sep:
        final_path = final_path.replace(os.sep, separator)

    return final_path

def get_parent_dir(file_obj: Union[TextIO, str], absolute: bool = False) -> str:
    """파일 객체 또는 파일 경로에서 디렉토리 경로를 추출합니다.

    Args:
        file_obj (Union[TextIO, str]): 파일 객체 또는 파일 경로.
        absolute (bool): True일 경우 절대 경로를 반환. 기본값은 False.

    Returns:
        str: 파일이 위치한 디렉토리 경로.
    """

    # 문자열 경로가 전달된 경우
    if isinstance(file_obj, str):
        dir_path = os.path.dirname(file_obj)
        return os.path.abspath(dir_path) if absolute else dir_path

    # 파일 객체가 전달된 경우
    elif hasattr(file_obj, 'name') and isinstance(file_obj.name, str):
        dir_path = os.path.dirname(file_obj.name)
        return os.path.abspath(dir_path) if absolute else dir_path

    # 유효하지 않은 타입인 경우
    else:
        raise ValueError("유효한 파일 객체 또는 파일 경로가 아닙니다.")


class FolderManager:
    def __init__(self, data: Union[str, TextIO], skip_dir: Optional[List[str]] = None, skip_type: Optional[List[str]] = None):
        str_path = data
        if isinstance(data, str):
            str_path = data
        # elif isinstance(data, TextIO)
        #     data.__dir__()

        if os.path.isdir(str_path):
            self.str_path = str_path
        else:
            self.str_path = get_parent_dir(str_path)

        # 제외할 폴더 및 파일 타입 설정
        self.skip_dir = skip_dir or []
        self.skip_type = skip_type or []

        # 폴더 및 파일 맵 초기화
        self.__sub_folder_map: Dict[str, List[str]] = {}
        self.__type_map: Dict[str, List[str]] = {}
        self.__file_list: List[str] = []  # 모든 파일 목록
        self.__dir_list: List[str] = []  # 모든 디렉토리 목록
        self.__file_map: Dict[str, List[str]] = {}  # 파일명별 파일 경로 맵
        self.__dir_map: Dict[str, List[str]] = {}  # 디렉토리명별 디렉토리 경로 맵
        self.__depth_map: Dict[int, Dict[str, List[str]]] = {}  # 깊이별 폴더와 파일 맵

        # 맵 생성 메서드 호출
        self._create_maps()

    def get_file_list(self) -> List[str]:
        return self.__file_list
    
    def get_dir_list(self) -> List[str]:
        return self.__dir_list
    
    def _create_maps(self):
        """폴더 내 파일과 폴더를 추적하여 sub_folder_map과 type_map을 생성하고,
           모든 파일과 폴더를 각각 file_list와 dir_list에 추가하며,
           파일명별 file_map과 디렉토리명별 dir_map도 생성합니다.
        """
        """맵 생성 시 skip_dir 및 skip_type 조건을 적용하여 초기화합니다."""
        for root, dirs, files in os.walk(self.str_path):
            if any(skip in root for skip in self.skip_dir):
                continue


            # 상대 경로 계산 및 깊이 산출
            relative_root = os.path.relpath(root, self.str_path)
            depth = relative_root.count(os.sep) + 1 if relative_root != "." else 0
            relative_root = "" if relative_root == "." else relative_root

            # depth_map 초기화 및 파일 추가
            if depth not in self.__depth_map:
                self.__depth_map[depth] = {}
            self.__depth_map[depth][relative_root] = [file for file in files]

            # dir_list 및 dir_map 업데이트
            self.__dir_list.append(relative_root)
            dir_name = os.path.basename(root)
            if dir_name not in self.__dir_map:
                self.__dir_map[dir_name] = []
            self.__dir_map[dir_name].append(root)

            # file_list 및 file_map 업데이트
            for file in files:
                file_relative_path = os.path.join(relative_root, file)
                self.__file_list.append(file_relative_path)
                if file not in self.__file_map:
                    self.__file_map[file] = []
                self.__file_map[file].append(file_relative_path)

                # 파일 타입별 추가
                file_extension = os.path.splitext(file)[1].lower()
                if file_extension not in self.__type_map:
                    self.__type_map[file_extension] = []
                self.__type_map[file_extension].append(file_relative_path)

    def get_sub_folder_map(self, skip_empty: bool = True, skip_dir: Optional[List[str]] = None,) -> Dict[
        str, List[str]]:
        """하위 폴더와 파일 리스트 맵을 반환하며, 특정 폴더를 제외하거나 빈 폴더를 제외할 수 있습니다.

        Args:
            skip_dir (Optional[List[str]]): 제외할 폴더 이름 리스트. 포함된 이름을 가진 폴더는 모두 제외합니다.
            skip_empty (bool): True일 경우 파일이 없는 빈 폴더를 제외합니다.

        Returns:
            Dict[str, List[str]]: 조건에 맞게 필터링된 하위 폴더와 파일 리스트 맵.
        """
        filtered_map = {}

        for folder, files in self.__sub_folder_map.items():
            # skip_dir에 있는 이름이 포함된 폴더는 제외
            if skip_dir and any(skip_name in folder for skip_name in skip_dir):
                continue

            # skip_empty가 True이고 파일이 없는 빈 폴더는 제외
            if skip_empty and not files:
                continue

            # 조건에 맞는 폴더만 추가
            filtered_map[folder] = files

        return filtered_map

    def get_type_map(self) -> Dict[str, List[str]]:
        """파일 타입별 파일 리스트 맵을 반환합니다."""
        return self.__type_map

    def get_file_map(self, min_count: int = 2) -> Dict[str, List[str]]:
        """파일명별 파일 리스트 맵을 반환하며, min_count 이상의 경로를 가진 파일만 포함합니다.

        Args:
            min_count (int): 해당 수 이상의 경로가 있는 파일만 포함. 기본값은 2.

        Returns:
            Dict[str, List[str]]: 파일명별 파일 리스트 맵.
        """
        return {file_name: paths for file_name, paths in self.__file_map.items() if len(paths) >= min_count}

    def get_dir_map(self, min_count: int = 2) -> Dict[str, List[str]]:
        """디렉토리명별 디렉토리 리스트 맵을 반환하며, min_count 이상의 경로를 가진 디렉토리만 포함합니다.

        Args:
            min_count (int): 해당 수 이상의 경로가 있는 디렉토리만 포함. 기본값은 2.

        Returns:
            Dict[str, List[str]]: 디렉토리명별 디렉토리 리스트 맵.
        """
        return {dir_name: paths for dir_name, paths in self.__dir_map.items() if len(paths) >= min_count}

    def get_depth_map(self, min_length: int = 1) -> Dict[int, Dict[str, List[str]]]:
        """깊이별 폴더와 파일 리스트 맵을 반환하며, 각 폴더에 min_length 이상의 파일이 있는 경우만 포함합니다.

        Args:
            min_length (int): 최소 포함할 파일 개수. 기본값은 1.

        Returns:
            Dict[int, Dict[str, List[str]]]: 필터링된 깊이별 폴더와 파일 리스트 맵.
        """
        filtered_depth_map = {}
        for depth, folders in self.__depth_map.items():
            filtered_folders = {folder: files for folder, files in folders.items() if len(files) >= min_length}
            if filtered_folders:  # 해당 깊이에 유효한 폴더가 있는 경우만 추가
                filtered_depth_map[depth] = filtered_folders
        return filtered_depth_map


    def __str__(self):
        return self.str_path


    def __repr__(self):
        return f'FolderManager({self.__str__()}, {len(self.__dir_list)} Dirs, {len(self.__file_list)} Files, {len(self.__depth_map)} depth))'

if __name__ == "__main__":
    import time
    # with open("../gdf", 'w') as file:
    #     print('w: ',type(file))
    #
    # with open("../log_reader////../filemanager\\../gdf", 'r') as file:
    #     print('r: ', type(file))
    #     print(file.name)
    #     print('extract_dir_from_file->', get_parent_dir(file))
    #     print('clean_path->', clean_path(get_parent_dir(file)))
    #
    #     print("extract folder to dir->", get_parent_dir(r'D:\dev\AutoPlanning\trunk\AP_trunk_pure'))
    #
    # print('=' * 100)
    st = time.time()
    mangaer = FolderManager(r'D:\dev\AutoPlanning\trunk\AP_trunk_pure', skip_dir=['.svn', 'external_dlls', 'external_libs', 'x64', 'vs'])
    # mangaer = FolderManager(r'../test_target_folder')

    ed = time.time()
    print(ed-st)

    st = time.time()
    sub_folder = mangaer.get_sub_folder_map(skip_dir=['.svn'])
    ed = time.time()
    print(ed-st)

    st = time.time()
    dir_map = mangaer.get_dir_map(min_count=2)
    ed = time.time()
    print(ed - st)

    st = time.time()
    file_map = mangaer.get_file_map(min_count=2)
    ed = time.time()
    print(ed - st)

    st = time.time()
    depth_map = mangaer.get_depth_map()
    ed = time.time()
    print(ed - st)


    print()

    print(mangaer)



