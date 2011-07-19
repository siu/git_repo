import util
import unittest
from pprint import pprint
import git_wrapper
from git_wrapper import GitWrapper
from mock import Mock

class GitWrapperTest(unittest.TestCase):
    def mock_git_cmd(self, return_value):
        self.git_cmd = Mock()
        self.git_cmd.return_value = return_value
        git_wrapper.execute_git_cmd = self.git_cmd

    def test_paths(self):
        self.repo = GitWrapper('bogus_repo')
        self.mock_git_cmd("sample_file.txt\ntest/test_a.py\n")

        assert('sample_file.txt' in self.repo.paths)
        assert('test/test_a.py' in self.repo.paths)

        self.git_cmd.assert_called_with('--git-dir=.git ls-files',
                self.repo.path)

    def test_stage_new_files(self):
        self.repo = GitWrapper('bogus_repo')
        self.mock_git_cmd("?? sample_file.txt\n?? second_sample_file.txt")

        assert('sample_file.txt' in self.repo.stage)
        assert('second_sample_file.txt' in self.repo.stage)
        assert(self.repo.stage['sample_file.txt'] == '??')
        assert(self.repo.stage['second_sample_file.txt'] == '??')

        self.git_cmd.assert_called_with('--git-dir=.git status --porcelain',
                self.repo.path)

    def test_stage_modified_file(self):
        self.repo = GitWrapper('bogus_repo')
        self.mock_git_cmd(" M sample_file.txt")

        assert('sample_file.txt' in self.repo.stage)
        assert(self.repo.stage['sample_file.txt'] == 'M')

        self.git_cmd.assert_called_with('--git-dir=.git status --porcelain',
                self.repo.path)

    def test_paths_different_git_dir(self):
        self.repo = GitWrapper('bogus_repo', '../bogus_repo.git')
        self.mock_git_cmd("sample_file.txt\ntest/test_a.py\n")

        assert self.repo.paths

        self.git_cmd.assert_called_with('--git-dir=../bogus_repo.git ls-files', 
                self.repo.path)
