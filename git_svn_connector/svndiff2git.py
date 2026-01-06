import svn_managers.svn_subprocess as SVNSubprocess
import git_managers.initializer as GitInitializer
import git_managers.adder as GitAdder

def main(path: str):
    modified_files: list[str] = SVNSubprocess.get_modified_files(path)
    print("Modified files in SVN:")
    print('file count : ', len(modified_files))

    GitInitializer.init_by_file_list(path, modified_files)
    GitAdder.add_ignore_file(path, ['.svn', '.vs', '.vscode', '.dll', '.obj'])
    GitAdder.add_by_path_list(path, modified_files)




if __name__ == "__main__":
    from filemanager.window_file_open import get_folder_path
    project_path = get_folder_path(title="프로젝트 폴더 선택")
    # project_path = r'D:\dev\AutoPlanning\trunk\Ap-Trunk-Auto-Tas

    main(project_path)