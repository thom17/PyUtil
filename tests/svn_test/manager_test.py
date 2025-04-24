import time

import svn_manager.svn_manager as SVNManager

project_path = r'D:\dev\AutoPlanning\trunk\AP_trunk_pure\mod_APImplantSimulation'
file_path = project_path + r'\UIDlgImplantLib.cpp'

def test_get_before_change_rv():
    print()
    # project_path = r'D:\dev\AutoPlanning\trunk\AP_trunk_pure\mod_APWorkSpace'
    # file_path = project_path + r'\ToolbarOrder.cpp'

    print("is project pulled ", SVNManager.is_pulled_path(project_path))
    print("is file_path pulled ", SVNManager.is_pulled_path(file_path))

    st = time.time()
    pj_rv = SVNManager.get_before_change_rv(path=project_path, revision=7641)
    ed = time.time()
    print(f'pj {(ed-st):.2f}')

    st = time.time()
    fi_rv = SVNManager.get_before_change_rv(path=file_path, revision=7641)
    ed = time.time()

    print(f'file_path {(ed-st):.2f}')

    print(pj_rv)
    print(fi_rv)

def test_none_before_change_rv():
    print('이전에 변경된 이력이 없는(중간에 추가된) 파일에 대하여 수행')
    file_path = r'D:\dev\AutoPlanning\trunk\AP_trunk_pure\mod_APImplantSimulation\DSimpleActuator.cpp'
    add_file_rv_num = 7581

    result = SVNManager.get_before_change_rv(path=file_path, revision= add_file_rv_num)
    print(result )


def test_do_update():
    print()
    project_path = r'D:\dev\AutoPlanning\trunk\AP_trunk_pure\mod_APImplantSimulation'
    file_path = project_path + r'\ToolbarOrder.cpp'

    # r = SVNManager.do_update(project_path)
    r = SVNManager.do_update(project_path, 7638)

    print(r)
    print(r)

def test_get_dif_map():
    print()
    project_path = r'D:\dev\AutoPlanning\trunk\AP_trunk_pure\mod_APImplantSimulation'
    file_path = project_path + r'\ActuatorPanoFixture.cpp'

    r = SVNManager.do_update(project_path, 7640)

    cur_rv = SVNManager.get_diif_map(path=project_path, revision=7640)
    # next_rv = SVNManager.get_diif_map(path=project_path, revision=7641)
    before_in_rv = SVNManager.get_diif_map(path=project_path, revision=7635)
    after_in_rv = SVNManager.get_diif_map(path=project_path, revision=7654)

    chs = SVNManager.make_block_changes(file_path, 7640)

    for dif_dict in cur_rv.values():
        diff = dif_dict['file_diff']
        bl_changes = SVNManager.make_block_changes(diff)
        print(bl_changes)

    print(r)
    print(r)


def test_check_rv_num():
    print()
    project_path = r'D:\dev\AutoPlanning\trunk\AP_trunk_pure\mod_APImplantSimulation'
    file_path = project_path + r'\ToolbarOrder.cpp'

    cur_rv = SVNManager.get_current_revision(project_path)
    repo_rv = SVNManager.get_head_revision(project_path)

    print(cur_rv)
    print(repo_rv)


def test_range_log_dif():
    print()
    st_t = time.time()
    project_path = r'D:\dev\AutoPlanning\trunk\AP_trunk_pure\mod_APImplantSimulation'
    start_rv = 7640
    r = SVNManager.get_svn_range_log_dif(path=project_path, start_revision=start_rv) #, end_revision=end_rv)
    print(r.keys())

    ed_t = time.time()
    print(ed_t-st_t)

def test_get_recent_logs():
    print()
    st_t = time.time()
    project_path = r'D:\dev\AutoPlanning\trunk\AP_trunk_pure'

    r = SVNManager.get_recent_logs(path=project_path)  # , end_revision=end_rv)
    print(r.keys())

    ed_t = time.time()
    print(ed_t - st_t)