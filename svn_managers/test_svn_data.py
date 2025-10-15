from unittest import TestCase
from svn_data import FileDiff

class TestFileDiff(TestCase):

    def test_get_svn_diff_files(self):
        path = r'D:\dev\AutoPlanning\Pano\pano-task\mod_APImplantSimulation'
        # path = r'D:\dev\AutoPlanning\Pano\pano-task\mod_APImplantSimulation\UIDlgImplantLib.cpp'
        result = FileDiff.from_subprocess(path, 7513)
        print(f'{type(result)} len {len(result)}')
        for dif in result:
            print(dif)



