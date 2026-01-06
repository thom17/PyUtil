import subprocess
import os
def add_by_path_list(path: str, file_path_lists: [str]):
    '''
    git add 명령어를 사용하여 파일들을 스테이징 영역에 추가하는 함수
    :param path: git 저장소의 루트 디렉토리 경로
    :param file_path_lists: 스테이징 영역에 추가할 파일들의 경로 리스트
    '''
    prev_path = os.getcwd()
    try:
        os.chdir(path) # git 명령어 실행을 위한 경로 변경
        for file_path in file_path_lists:
            add_cmd = ['git', 'add', file_path]
            result = subprocess.run(add_cmd, capture_output=True, text=True)

            if result.returncode == 0:
                print(f"Added:  {file_path}")
            else:
                print(f"Failed to add {file_path}: {result.stderr}")

        # # 4. Git status 확인
        # git_status_cmd = ["git", "status", "--short"]
        # result = subprocess.run(git_status_cmd, capture_output=True, text=True)
        # print("\nGit status:")
        # print(result.stdout)
        # return result
    except Exception as e:
        print(f'Error during git operations: {e}')

    finally:
        # 이전 경로로 복귀
        os.chdir(prev_path)

def add_ignore_file(path, ignore_patterns: list[str]):
    '''
    .gitignore 파일 생성
    :param path:
    :param ignore_patterns:
    :return:
    '''
    if os.path.exists(os.path.join(path, '.gitignore')):
        print(f'Error : .gitignore already exists in {path}')
        return False


    gitignore_path = os.path.join(path, '.gitignore')
    try:
        with open(gitignore_path, 'w') as gitignore_file:
            for pattern in ignore_patterns:
                gitignore_file.write(pattern + '\n')
        print(f'.gitignore file created at {gitignore_path}')
        return True
    except Exception as e:
        print(f'Error creating .gitignore file: {e}')
        return False