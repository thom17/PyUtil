import pytest

from svn_manager.svn_manager import get_line_changes_log_map

import svn_manager.svn_data_factory as svnFactory

project_path = r'D:\dev\AutoPlanning\Pano\pano-task\mod_APImplantSimulation'
simpleCppPath = project_path + r'\DSimpleActuator.cpp'

cpp_diff = svnFactory.make_fileDiff(simpleCppPath, 7555)
project_diff = svnFactory.make_fileDiff(project_path, 7555)


path = r'D:\dev\AutoPlanning\Pano\pano-task\mod_APImplantSimulation'
# logs_map = get_svn_logs(path)
print('done')

line_change_map = get_line_changes_log_map(file_path=simpleCppPath)
print(len(line_change_map))