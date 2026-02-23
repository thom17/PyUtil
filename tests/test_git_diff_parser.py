import os
import re
import sys
import unittest
from unittest.mock import patch, MagicMock

# git_managers 모듈 임포트를 위해 경로 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from git_managers.git_diff_data import Change, Hunk, GitFileChange
from git_managers.git_diff_parser import GitDiffParser
from git_managers.git_line_apply import (
    filter_changes_by_content,
    filter_changes_by_line_numbers,
    generate_partial_patch,
    apply_partial_patch,
    preview_changes,
)

# 샘플 git diff 출력 문자열
SAMPLE_DIFF = """\
diff --git a/src/main.py b/src/main.py
index abc1234..def5678 100644
--- a/src/main.py
+++ b/src/main.py
@@ -1,5 +1,6 @@
 def hello():
-    print("Hello")
+    print("Hello, World!")
+    # 안녕하세요
     return True
 
 def bye():
"""

# 한글이 포함된 diff
KOREAN_DIFF = """\
diff --git a/module/utils.py b/module/utils.py
index 111aaaa..222bbbb 100644
--- a/module/utils.py
+++ b/module/utils.py
@@ -10,7 +10,8 @@
 def process():
-    # old comment
+    # 새로운 주석 (한글 포함)
+    result = calculate()
     return result
 
 def cleanup():
@@ -20,4 +21,4 @@
 def finish():
-    pass
+    print("완료")
     return 0
"""


class TestGitDiffData(unittest.TestCase):
    def test_change_repr(self):
        change = Change(5, "hello world")
        self.assertIn("5", repr(change))
        self.assertIn("hello world", repr(change))

    def test_hunk_repr(self):
        hunk = Hunk(1, 1)
        self.assertIn("old_start=1", repr(hunk))
        self.assertIn("new_start=1", repr(hunk))

    def test_hunk_print_info(self):
        hunk = Hunk(1, 1)
        hunk.added.append(Change(2, "added line"))
        hunk.removed.append(Change(1, "removed line"))
        hunk.old_line = 2
        hunk.new_line = 3
        # 출력이 예외 없이 실행되는지 확인
        hunk.print_info()

    def test_git_file_change_add_hunk(self):
        fc = GitFileChange("src/test.py", "abc123")
        hunk = Hunk(1, 1)
        fc.add_hunk(hunk)
        self.assertEqual(len(fc.hunks), 1)

    def test_get_all_change_pair(self):
        fc = GitFileChange("src/test.py", "abc123")
        hunk = Hunk(1, 1)
        hunk.added.append(Change(2, "new line"))
        hunk.removed.append(Change(1, "old line"))
        fc.add_hunk(hunk)

        del_changes, add_changes = fc.get_all_change_pair()
        self.assertEqual(len(del_changes), 1)
        self.assertEqual(len(add_changes), 1)
        self.assertEqual(del_changes[0].content, "old line")
        self.assertEqual(add_changes[0].content, "new line")


class TestGitDiffParser(unittest.TestCase):
    def test_parse_sample_diff(self):
        parser = GitDiffParser(SAMPLE_DIFF, "abc123")
        self.assertEqual(len(parser.changes), 1)

        fc = parser.changes[0]
        self.assertEqual(fc.file_path, "src/main.py")
        self.assertEqual(len(fc.hunks), 1)

    def test_parse_hunk_lines(self):
        parser = GitDiffParser(SAMPLE_DIFF, "abc123")
        hunk = parser.changes[0].hunks[0]

        # 제거된 줄: print("Hello")
        self.assertEqual(len(hunk.removed), 1)
        self.assertIn('print("Hello")', hunk.removed[0].content)

        # 추가된 줄: print("Hello, World!") 와 # 안녕하세요
        self.assertEqual(len(hunk.added), 2)

    def test_parse_korean_diff(self):
        parser = GitDiffParser(KOREAN_DIFF, "def456")
        self.assertEqual(len(parser.changes), 1)

        fc = parser.changes[0]
        self.assertEqual(fc.file_path, "module/utils.py")
        self.assertEqual(len(fc.hunks), 2)

    def test_parse_korean_content(self):
        parser = GitDiffParser(KOREAN_DIFF, "def456")
        fc = parser.changes[0]
        del_changes, add_changes = fc.get_all_change_pair()

        # 한글이 포함된 추가 라인 확인
        added_contents = [c.content for c in add_changes]
        korean_lines = [c for c in added_contents if re.search(r'[가-힣]', c)]
        self.assertGreater(len(korean_lines), 0)

    def test_parse_empty_diff(self):
        parser = GitDiffParser('', 'abc123')
        self.assertEqual(len(parser.changes), 0)

    @patch('subprocess.run')
    def test_get_diff_static(self, mock_run):
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = SAMPLE_DIFF
        mock_run.return_value = mock_result

        parser = GitDiffParser.GetDiff('/repo', 'abc123')
        self.assertEqual(len(parser.changes), 1)
        mock_run.assert_called_once()

    @patch('subprocess.run')
    def test_get_diff_range_static(self, mock_run):
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = KOREAN_DIFF
        mock_run.return_value = mock_result

        parser = GitDiffParser.GetDiffRange('/repo', 'abc000', 'def456')
        self.assertEqual(len(parser.changes), 1)
        mock_run.assert_called_once()

    @patch('subprocess.run')
    def test_get_diff_error(self, mock_run):
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = ''
        mock_result.stderr = 'fatal: not a git repo'
        mock_run.return_value = mock_result

        parser = GitDiffParser.GetDiff('/not-a-repo', 'abc123')
        self.assertEqual(len(parser.changes), 0)


class TestFilterFunctions(unittest.TestCase):
    def setUp(self):
        self.parser = GitDiffParser(KOREAN_DIFF, "def456")
        self.fc = self.parser.changes[0]

    def test_filter_by_content_korean(self):
        del_changes, add_changes = filter_changes_by_content(self.fc, r'[가-힣]')
        # 한글이 포함된 추가 라인이 존재해야 함
        self.assertGreater(len(add_changes), 0)
        for change in add_changes:
            self.assertRegex(change.content, r'[가-힣]')

    def test_filter_by_content_no_match(self):
        del_changes, add_changes = filter_changes_by_content(self.fc, r'ZZZNOMATCH')
        self.assertEqual(len(del_changes), 0)
        self.assertEqual(len(add_changes), 0)

    def test_filter_by_line_numbers(self):
        all_del, all_add = self.fc.get_all_change_pair()
        if all_add:
            target_line = all_add[0].line_number
            _, add_changes = filter_changes_by_line_numbers(self.fc, [target_line])
            self.assertEqual(len(add_changes), 1)
            self.assertEqual(add_changes[0].line_number, target_line)

    def test_filter_by_line_numbers_empty(self):
        del_changes, add_changes = filter_changes_by_line_numbers(self.fc, [99999])
        self.assertEqual(len(del_changes), 0)
        self.assertEqual(len(add_changes), 0)


class TestGeneratePatch(unittest.TestCase):
    def setUp(self):
        self.parser = GitDiffParser(SAMPLE_DIFF, "abc123")
        self.fc = self.parser.changes[0]

    def test_generate_partial_patch_creates_file(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            patch_path = os.path.join(tmpdir, 'test.patch')
            _, add_changes = self.fc.get_all_change_pair()
            keep_lines = [c.line_number for c in add_changes]
            generate_partial_patch(self.fc, keep_lines, patch_path)
            self.assertTrue(os.path.exists(patch_path))
            with open(patch_path, 'r', encoding='utf-8') as f:
                content = f.read()
            self.assertIn('--- a/', content)
            self.assertIn('+++ b/', content)

    @patch('subprocess.run')
    def test_apply_partial_patch_success(self, mock_run):
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = ''
        mock_result.stderr = ''
        mock_run.return_value = mock_result

        apply_partial_patch('/repo', '/tmp/test.patch')
        mock_run.assert_called_once()

    @patch('subprocess.run')
    def test_apply_partial_patch_failure(self, mock_run):
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = ''
        mock_result.stderr = 'patch does not apply'
        mock_run.return_value = mock_result

        # 예외 없이 실행되어야 함
        apply_partial_patch('/repo', '/tmp/test.patch')
        mock_run.assert_called_once()


class TestPreviewChanges(unittest.TestCase):
    def test_preview_no_filter(self):
        parser = GitDiffParser(SAMPLE_DIFF, "abc123")
        fc = parser.changes[0]
        # 예외 없이 실행되어야 함
        preview_changes(fc)

    def test_preview_with_filter(self):
        parser = GitDiffParser(KOREAN_DIFF, "def456")
        fc = parser.changes[0]

        def korean_filter(file_change):
            return filter_changes_by_content(file_change, r'[가-힣]')

        preview_changes(fc, filter_func=korean_filter)


if __name__ == '__main__':
    unittest.main()
