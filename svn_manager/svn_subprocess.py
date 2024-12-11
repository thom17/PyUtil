'''
공통적으로 또는 메서드 하나 수준으로 사용할만한 유틸 모듈
'''

import subprocess
import xml.etree.ElementTree as ET
from typing import Optional, Union, List, Dict
from datetime import datetime
from collections import defaultdict


def get_repo_url(file_path: str) -> str:
    """
    로컬 경로에서 리포지토리 URL을 얻는다.
    """
    command = ["svn", "info", file_path]
    # print("Executing command:", " ".join(command))  # 명령 출력

    try:
        # 명령 실행
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode == 0:
            # `svn info`의 결과에서 URL 추출
            for line in result.stdout.splitlines():
                if line.startswith("URL:"):
                    repo_url = line.split("URL:")[1].strip()
                    # print(f"Repository URL: {repo_url}")
                    return repo_url
            raise ValueError("URL not found in svn info output")
        else:
            print("Error:\n", result.stderr)
            raise RuntimeError(f"Failed to get SVN info for {file_path}")
    except Exception as e:
        print("An error occurred:", e)
        raise


def get_file_at_revision(file_path: str, revision: int) -> str:
    repo_url = get_repo_url(file_path)

    # SVN cat 명령어 생성
    command = ["svn", "cat", "-r", str(revision), repo_url]
    # print("Executing command:", " ".join(command))  # 명령 출력

    try:
        # 명령 실행
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode == 0:
            # print(f"Contents of {repo_url} at revision {revision}:\n")
            return result.stdout
        else:
            print("Error:\n", result.stderr)
    except Exception as e:
        print("An error occurred:", e)


def do_update(path: str, revision: Union[int, str] = 'HEAD') -> Dict[str, List[str]]:
    """
    Update the given path to the specified revision and return the list of updated files.

    Args:
        path (str): The file or directory path to update.
        revision (Union[int, str]): The revision number or 'HEAD' for the latest revision.

    Returns:
        List[str]: A list of paths that were updated or changed.
    """
    # Build the SVN update command
    command = ["svn", "update", "-r", str(revision), path]
    print("Executing command:", " ".join(command))

    updated_files_map = defaultdict(list)

    try:
        # Run the SVN update command
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        # Check the result
        if result.returncode == 0:
            print("Update successful!")
            print("Output:\n", result.stdout)

            # Parse updated file paths from the output
            for line in result.stdout.splitlines():
                if line.startswith(('A ', 'U ', 'D ', 'R ')):  # Check for SVN status indicators
                    mod, file_path = line.split()
                    updated_files_map[mod].append(file_path) # Extract the file path

        else:
            print("Error during update:")
            print("Error message:\n", result.stderr)
    except Exception as e:
        print(f"An exception occurred: {e}")
    finally:
        return dict(updated_files_map)