import re
import subprocess
import os

from typing import List, Callable, Optional

from git_managers.git_diff_data import GitFileChange, Change
from git_managers.git_diff_parser import GitDiffParser


def filter_changes_by_content(file_change: GitFileChange, pattern: str):
    """
    정규식 패턴으로 변경 라인 필터링.
    패턴에 매칭되는 라인을 포함하는 hunk만 반환.

    Args:
        file_change (GitFileChange): 파싱된 파일 변경 정보
        pattern (str): 정규식 패턴 (예: '[가-힣]' 한글 포함 라인)

    Returns:
        Tuple[List[Change], List[Change]]: (필터된 del_changes, 필터된 add_changes)
    """
    compiled = re.compile(pattern)
    del_changes = []
    add_changes = []

    for hunk in file_change.hunks:
        for change in hunk.removed:
            if compiled.search(change.content):
                del_changes.append(change)
        for change in hunk.added:
            if compiled.search(change.content):
                add_changes.append(change)

    return del_changes, add_changes


def filter_changes_by_line_numbers(file_change: GitFileChange, line_numbers: List[int]):
    """
    특정 라인 번호의 변경사항만 필터링.

    Args:
        file_change (GitFileChange): 파싱된 파일 변경 정보
        line_numbers (List[int]): 필터링할 라인 번호 목록

    Returns:
        Tuple[List[Change], List[Change]]: (필터된 del_changes, 필터된 add_changes)
    """
    line_set = set(line_numbers)
    del_changes = []
    add_changes = []

    for hunk in file_change.hunks:
        for change in hunk.removed:
            if change.line_number in line_set:
                del_changes.append(change)
        for change in hunk.added:
            if change.line_number in line_set:
                add_changes.append(change)

    return del_changes, add_changes


def generate_partial_patch(file_change: GitFileChange, keep_lines: List[int], patch_path: str):
    """
    선택한 라인만 포함하는 패치 파일 생성.

    Args:
        file_change (GitFileChange): 파싱된 파일 변경 정보
        keep_lines (List[int]): 포함할 new 라인 번호 목록 (추가 라인 기준)
        patch_path (str): 저장할 패치 파일 경로
    """
    keep_set = set(keep_lines)
    patch_lines = []

    patch_lines.append(f"--- a/{file_change.file_path}\n")
    patch_lines.append(f"+++ b/{file_change.file_path}\n")

    for hunk in file_change.hunks:
        hunk_body = []
        add_count = 0
        del_count = 0

        # 각 hunk 내 변경 라인을 old/new 라인 번호 순서대로 재구성
        old_cur = hunk.old_start
        new_cur = hunk.new_start

        removed_map = {c.line_number: c for c in hunk.removed}
        added_map = {c.line_number: c for c in hunk.added}

        max_old = hunk.old_line
        max_new = hunk.new_line

        while old_cur < max_old or new_cur < max_new:
            if old_cur in removed_map and new_cur in added_map:
                # 변경(제거 후 추가)
                if new_cur in keep_set:
                    hunk_body.append(f"-{removed_map[old_cur].content}\n")
                    del_count += 1
                    hunk_body.append(f"+{added_map[new_cur].content}\n")
                    add_count += 1
                else:
                    hunk_body.append(f" {removed_map[old_cur].content}\n")
                old_cur += 1
                new_cur += 1
            elif old_cur in removed_map:
                if old_cur in keep_set:
                    hunk_body.append(f"-{removed_map[old_cur].content}\n")
                    del_count += 1
                else:
                    hunk_body.append(f" {removed_map[old_cur].content}\n")
                old_cur += 1
            elif new_cur in added_map:
                if new_cur in keep_set:
                    hunk_body.append(f"+{added_map[new_cur].content}\n")
                    add_count += 1
                new_cur += 1
            else:
                # context 라인 (실제 내용은 없으나 카운터만 증가)
                old_cur += 1
                new_cur += 1

        if add_count > 0 or del_count > 0:
            old_count = hunk.old_line - hunk.old_start
            new_count = hunk.new_line - hunk.new_start
            patch_lines.append(f"@@ -{hunk.old_start},{old_count} +{hunk.new_start},{new_count} @@\n")
            patch_lines.extend(hunk_body)

    try:
        os.makedirs(os.path.dirname(patch_path), exist_ok=True)
        with open(patch_path, 'w', encoding='utf-8') as f:
            f.writelines(patch_lines)
    except Exception as e:
        print(f"패치 파일 생성 오류: {e}")


def apply_partial_patch(repo_path: str, patch_path: str):
    """
    생성된 패치를 git apply로 적용.

    Args:
        repo_path (str): 저장소 경로
        patch_path (str): 패치 파일 경로
    """
    command = ["git", "-C", repo_path, "apply", patch_path]
    try:
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            encoding='utf-8', errors='replace'
        )
        if result.returncode == 0:
            print("패치 적용 성공")
        else:
            print(f"패치 적용 실패: {result.stderr}")
    except Exception as e:
        print(f"Exception running git apply: {e}")


def revert_lines(repo_path: str, commit_hash: str, file_path: str, line_numbers: List[int]):
    """
    특정 커밋에서 특정 라인만 되돌리기.
    내부적으로 reverse diff를 생성하고 해당 라인만 포함하는 패치를 만들어 적용.

    Args:
        repo_path (str): 저장소 경로
        commit_hash (str): 대상 커밋 해시
        file_path (str): 파일 경로
        line_numbers (List[int]): 되돌릴 라인 번호 목록
    """
    # reverse diff 생성: <commit> -> <commit>~1 방향
    command = ["git", "-C", repo_path, "diff", commit_hash, f"{commit_hash}~1", "--", file_path]
    try:
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            encoding='utf-8', errors='replace'
        )
        if result.returncode != 0:
            print(f"reverse diff 생성 실패: {result.stderr}")
            return

        from git_managers.git_diff_parser import GitDiffParser
        parser = GitDiffParser(result.stdout, commit_hash)
        if not parser.changes:
            print("변경 사항 없음")
            return

        file_change = parser.changes[0]
        patch_path = os.path.join(repo_path, '.git', 'partial_revert.patch')
        generate_partial_patch(file_change, line_numbers, patch_path)
        apply_partial_patch(repo_path, patch_path)

    except Exception as e:
        print(f"revert_lines 오류: {e}")


def preview_changes(file_change: GitFileChange, filter_func: Optional[Callable] = None):
    """
    변경사항을 사람이 읽기 쉬운 형태로 출력.

    Args:
        file_change (GitFileChange): 파싱된 파일 변경 정보
        filter_func (Callable, optional): 필터 함수. (file_change) -> (del_changes, add_changes) 형태.
    """
    print(f"파일: {file_change.file_path}")

    if filter_func:
        del_changes, add_changes = filter_func(file_change)
    else:
        del_changes, add_changes = file_change.get_all_change_pair()

    print(f"  삭제 라인 수: {len(del_changes)}")
    for change in del_changes:
        print(f"  -{change.line_number}: {change.content}")

    print(f"  추가 라인 수: {len(add_changes)}")
    for change in add_changes:
        print(f"  +{change.line_number}: {change.content}")
    print()
