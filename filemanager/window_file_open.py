import tkinter as tk
from tkinter import filedialog

from typing import Union, List

def get_folder_path(title: str = '폴더 선택') -> str:
    """윈도우 탐색기를 통해 폴더를 선택하고 해당 경로를 반환합니다.

    Args:
        title (str): 폴더 선택 창의 제목. 기본값은 '폴더 선택'.

    Returns:
        str: 선택된 폴더의 절대 경로. 취소시 빈 문자열 반환.
    """
    # tkinter root 윈도우 생성 및 숨김
    root = tk.Tk()
    root.withdraw()

    # 폴더 선택 다이얼로그 표시
    folder_path = filedialog.askdirectory(
        title=title,
        initialdir='/'  # 초기 디렉토리를 루트로 설정
    )

    return folder_path
def get_file_path(file_types: List[str] = None, multiple: bool = False, title: str = '파일 선택') -> Union[str, tuple]:
    """윈도우 탐색기를 통해 파일을 선택하고 해당 경로를 반환합니다.
    
    Args:
        file_types (list, optional): 파일 형식 필터 리스트. 예: [('텍스트 파일','*.txt'), ('모든 파일','*.*')]
        multiple (bool, optional): True일 경우 다중 파일 선택 가능. 기본값은 False.
        title (str, optional): 파일 선택 창의 제목. 기본값은 '파일 선택'.
    
    Returns:
        Union[str, tuple]: multiple이 False인 경우 선택된 파일의 절대 경로 문자열,
                          True인 경우 선택된 파일들의 절대 경로 튜플. 취소시 빈 문자열 또는 빈 튜플 반환.
    """
    # tkinter root 윈도우 생성 및 숨김
    root = tk.Tk()
    root.withdraw()

    # 기본 파일 형식 필터 설정
    if file_types is None:
        file_types = [('모든 파일','*.*')]

    # 파일 선택 다이얼로그 표시
    if multiple:
        file_path = filedialog.askopenfilenames(
            title=title,
            filetypes=file_types,
            initialdir='/'  # 초기 디렉토리를 루트로 설정
        )
    else:
        file_path = filedialog.askopenfilename(
            title=title,
            filetypes=file_types,
            initialdir='/'  # 초기 디렉토리를 루트로 설정
        )

    return file_path
if __name__ == "__main__":
    print(get_folder_path(title='window_file_open.py Test : get_folder_path'))
    print(get_file_path(title='window_file_open.py Test : get_file_path'))
    print(get_file_path(multiple=True, title='window_file_open.py Test : get_file_path multiple'))
