'''
공통적으로 또는 메서드 하나 수준으로 사용할만한 유틸 모듈
'''

import subprocess
import xml.etree.ElementTree as ET
from typing import Optional
from datetime import datetime


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
