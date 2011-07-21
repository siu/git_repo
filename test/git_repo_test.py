import util
import unittest

import git_repo
from mock import Mock

class GitRepoBaseTest(unittest.TestCase):
    def mock_git_cmd(self, return_value):
        self.git_cmd = Mock()
        self.git_cmd.return_value = return_value
        git_repo.execute_git_cmd = self.git_cmd

class GitRepoTest(GitRepoBaseTest):
    def setUp(self):
        self.repo = git_repo.GitRepo('bogus_repo')

    def test_paths(self):
        self.mock_git_cmd("sample_file.txt\ntest/test_a.py")

        self.assertEqual(self.repo.paths, ['sample_file.txt', 'test/test_a.py'])

        self.git_cmd.assert_called_with('--git-dir=".git" ls-files',
                self.repo.path)

    def test_staging_new_files(self):
        self.mock_git_cmd("")

        self.assertEqual(self.repo.staging, {})

        self.git_cmd.assert_called_with('--git-dir=".git" status --porcelain',
                self.repo.path)

    def test_staging_new_files(self):
        self.mock_git_cmd("?? sample_file.txt\n?? second_sample_file.txt")

        self.assertEqual(self.repo.staging, {
            'sample_file.txt': '??', 
            'second_sample_file.txt': '??'
            })

        self.git_cmd.assert_called_with('--git-dir=".git" status --porcelain',
                self.repo.path)

    def test_staging_modified_file(self):
        self.mock_git_cmd(" M sample_file.txt")

        self.assertEqual(self.repo.staging, { 'sample_file.txt': 'M' })

        self.git_cmd.assert_called_with('--git-dir=".git" status --porcelain',
                self.repo.path)

    def test_commit_quotes_message(self):
        self.mock_git_cmd("")

        self.repo.commit('unquoted message')

        self.git_cmd.assert_called_with(
                '--git-dir=".git" commit -m "unquoted message"',
                self.repo.path)

    def test_add_all(self):
        self.mock_git_cmd("?? sample_file.txt\n?? second_sample_file.txt")
        add = Mock()
        self.repo.add = add

        self.repo.add_all()

        self.assertEqual(add.call_args_list, [
                (('sample_file.txt',), {}),
                (('second_sample_file.txt',), {})
            ])

class GitRepoExternalGitDirTest(GitRepoBaseTest):
    def setUp(self):
        self.repo = git_repo.GitRepo('bogus_repo', '../bogus_repo.git')

    def test_paths_different_git_dir(self):
        self.mock_git_cmd("sample_file.txt\ntest/test_a.py\n")

        assert self.repo.paths

        self.git_cmd.assert_called_with('--git-dir="../bogus_repo.git" ls-files', 
                self.repo.path)
