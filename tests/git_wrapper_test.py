import unittest
from pprint import pprint
import git_wrapper
from git_wrapper import GitWrapper
from mock import Mock

class GitWrapperIntegrationTest(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_paths(self):
        project_path = 'bogus_folder'

        git = Mock()
        git.return_value = "sample_file.txt\ntest/test_a.py\n"
        git_wrapper.execute_git_cmd = git

        git_project = GitWrapper(project_path)

        assert('sample_file.txt' in git_project.paths)
        assert('test/test_a.py' in git_project.paths)
        git.assert_called_with('--git-dir=.git ls-files',
                project_path)

    def test_stage_new_files(self):
        project_path = 'bogus_folder'

        git = Mock()
        git.return_value = "?? sample_file.txt\n?? second_sample_file.txt"
        git_wrapper.execute_git_cmd = git

        git_project = GitWrapper(project_path)

        assert('sample_file.txt' in git_project.stage)
        assert('second_sample_file.txt' in git_project.stage)
        assert(git_project.stage['sample_file.txt'] == '??')
        assert(git_project.stage['second_sample_file.txt'] == '??')
        git.assert_called_with('--git-dir=.git status --porcelain',
                project_path)

    def test_stage_modified_file(self):
        project_path = 'bogus_folder'

        git = Mock()
        git.return_value = " M sample_file.txt"
        git_wrapper.execute_git_cmd = git

        git_project = GitWrapper(project_path)

        assert('sample_file.txt' in git_project.stage)
        assert(git_project.stage['sample_file.txt'] == 'M')
        git.assert_called_with('--git-dir=.git status --porcelain',
                project_path)

    def test_paths_different_git_dir(self):
        project_path = 'bogus_folder'

        git = Mock()
        git.return_value = "sample_file.txt\ntest/test_a.py\n"
        git_wrapper.execute_git_cmd = git

        git_project = GitWrapper(project_path, '../bogus_folder.git')

        assert git_project.paths

        git.assert_called_with('--git-dir=../bogus_folder.git ls-files',
                project_path)
