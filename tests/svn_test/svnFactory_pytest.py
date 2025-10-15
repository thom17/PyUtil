import pytest
from dataclasses import asdict

from svn_managers.svn_manager import get_line_changes_log_map

import svn_managers.svn_data_factory as svnFactory

import svn_managers.svn_manager as SVN

def test_t1():
    project_path = r'D:\dev\AutoPlanning\Pano\pano-task\mod_APImplantSimulation'
    simpleCppPath = project_path + r'\DSimpleActuator.cpp'

    cpp_diff = svnFactory.make_fileDiff(simpleCppPath, 7555)
    project_diff = svnFactory.make_fileDiff(project_path, 7555)


    path = r'D:\dev\AutoPlanning\Pano\pano-task\mod_APImplantSimulation'
    # logs_map = get_svn_logs(path)
    print('done')

    line_change_map = get_line_changes_log_map(file_path=simpleCppPath)
    print(len(line_change_map))

def test_get_rv_file():
    print()
    file_path = r'D:\dev\AutoPlanning\trunk\AP_trunk_pure\mod_APImplantSimulation\UIDlgImplantLib.cpp'
    rv_edit_list = [7587, 7586, 7581, 7302]

    print(SVN.get_file_at_revision(file_path, 7581))

def test_factory():
    file_path = r'D:\dev\AutoPlanning\trunk\AP_trunk_pure\mod_APImplantSimulation\UIDlgImplantLib.cpp'

    file_diff = svnFactory.make_fileDiff(file_path, 7581)[0]
    di = file_diff.to_dict()
    di2 = asdict(file_diff)
    # di3 = asdict(di2)

    print(di)
    print(di2)
    # print(di3)
