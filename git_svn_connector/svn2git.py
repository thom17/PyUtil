import os.path


import svn_managers.svn_manager as SVNManager
import git_managers.initializer as GitInitializer
import git_managers.adder as GitAdder

#svn 기준 수정된 로컬 파일을 git으로 초기화
def svn_status_2_git_init(svn_path: str, git_path: str = '', status_filters : list[str] = ["M"]):
    modified_files: list[str] = SVNManager.get_modified_files(svn_path, status_filters)
    print("Modified files in SVN:")
    print('file count : ', len(modified_files))

    if not git_path:
        git_path = svn_path

    assert git_path in svn_path, 'Git 저장소 내부에 SVN 작업 경로가 위치해야함 '


    GitInitializer.init_by_file_list(git_path, modified_files)
    GitAdder.add_ignore_file(git_path, ['.svn', '.vs', '.vscode', '.dll', '.obj'])
    GitAdder.add_by_path_list(git_path, modified_files)

#svn 기준
def svn_2_git(svn_path: str, git_path: str = '', visit_dir: bool = True):
    if not git_path:
        git_path = svn_path
    assert git_path in svn_path, 'Git 저장소 내부에 SVN 작업 경로가 위치해야함 '

    file_list = SVNManager.get_list(svn_path, visit_dir)
    print(f"Visit Dir : {visit_dir} Svn Path : {svn_path}")
    print('list count : ', len(file_list))
    print('git path : ', git_path)

    file_list = [os.path.normpath(os.path.join(svn_path, f)) for f in file_list]

    GitInitializer.init_by_file_list(git_path, file_list)
    GitAdder.add_ignore_file(git_path, ['.svn', '.vs', '.vscode', '.dll', '.obj'])
    GitAdder.add_by_path_list(git_path, file_list)




if __name__ == "__main__":
    from filemanager.window_file_open import get_folder_path
    project_path = get_folder_path(title="프로젝트 폴더 선택")
    # project_path = r'D:\dev\AutoPlanning\trunk\Ap-Trunk-Auto-Tas

    project = os.path.dirname(project_path)
    # svn_status_2_git_init(project_path, git_path=project)

    svn_2_git(project_path)