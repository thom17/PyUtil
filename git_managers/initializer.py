'''
init
'''
import subprocess
import os
def init_by_file_list(path, file_path_lists: list[str]):
    '''
    git 초기화
    :param path:
    :param add file_lists:
    :return:
    '''
    if os.path.exists(os.path.join(path, '.git')):
        print(f'Error : git already initialized in {path}')
        return False

    init_cmd = ['git', 'init', path]
    result = subprocess.run(init_cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f'Error initializing git repository: {result.stderr}')
        return False

    #현제 cmd 경로 저장
    prev_path = os.getcwd()



    return True

