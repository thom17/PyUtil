import svn_manager.svn_subprocess as SVNSubprocess

def test_do_update():
    print()
    path = r'D:\\dev\\AutoPlanning\\trunk\\AP_trunk_pure\\mod_APImplantSimulation'
    start_rv = '7246'

    di1 = SVNSubprocess.do_update(path)
    di2 = SVNSubprocess.do_update(path, revision=start_rv)
    di3 = SVNSubprocess.do_update(path)

    print()