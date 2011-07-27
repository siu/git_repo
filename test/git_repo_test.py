# -*- coding: utf-8 -*-

import util
import unittest

import datetime

import git_repo
from mock import Mock

class GitRepoBaseTest(unittest.TestCase):
    def mock_git_cmd(self, return_value):
        self.git_cmd = Mock()
        self.git_cmd.return_value = return_value
        git_repo.execute_git_cmd = self.git_cmd

class GitRepoTest(GitRepoBaseTest):
    def setUp(self):
        self.maxDiff = None
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

    def test_log(self):
        self.mock_git_cmd("""commit f2d2cc3b4e84104b5ca4cae16a07f8b924d2bb06
Author: David Siñuela Pastor <siu.4coders@gmail.com>
Date:   Thu Jul 21 09:39:48 2011 +0200

    Don't commit in test_add_all integration test

commit 018825f04b0f58f3f9b852da3e21f9e84441d657
Author: David Siñuela Pastor <siu.4coders@gmail.com>
Date:   Thu Jul 20 09:39:48 2011 +0200

    Add README.md""")
        self.assertEqual([
            {
            'Commit': 'f2d2cc3b4e84104b5ca4cae16a07f8b924d2bb06',
            'Author': 'David Siñuela Pastor <siu.4coders@gmail.com>',
            'Date': datetime.datetime(2011, 7, 21, 9, 39, 48),
            'Title': 'Don\'t commit in test_add_all integration test',
            'Message': 'Don\'t commit in test_add_all integration test',
            },
            {
            'Commit': '018825f04b0f58f3f9b852da3e21f9e84441d657',
            'Author': 'David Siñuela Pastor <siu.4coders@gmail.com>',
            'Date': datetime.datetime(2011, 7, 20, 9, 39, 48),
            'Title': 'Add README.md',
            'Message': 'Add README.md'
            }], self.repo.log)
        self.git_cmd.assert_called_with(
                '--git-dir=".git" log --format=medium',
                self.repo.path)

    def test_single_log(self):
        self.mock_git_cmd("""commit f2d2cc3b4e84104b5ca4cae16a07f8b924d2bb06
Author: David Siñuela Pastor <siu.4coders@gmail.com>
Date:   Thu Jul 21 09:39:48 2011 +0200

    Don't commit in test_add_all integration test""")
        self.assertEqual([
            {
            'Commit': 'f2d2cc3b4e84104b5ca4cae16a07f8b924d2bb06',
            'Author': 'David Siñuela Pastor <siu.4coders@gmail.com>',
            'Date': datetime.datetime(2011, 7, 21, 9, 39, 48),
            'Title': 'Don\'t commit in test_add_all integration test',
            'Message': 'Don\'t commit in test_add_all integration test'
            }], self.repo.log)
        self.git_cmd.assert_called_with(
                '--git-dir=".git" log --format=medium',
                self.repo.path)

    def test_multiline_log(self):
        self.mock_git_cmd("""commit f2d2cc3b4e84104b5ca4cae16a07f8b924d2bb06
Author: David Siñuela Pastor <siu.4coders@gmail.com>
Date:   Thu Jul 21 09:39:48 2011 +0200

    Don't commit in test_add_all integration test
    Not needed

commit 018825f04b0f58f3f9b852da3e21f9e84441d657
Author: David Siñuela Pastor <siu.4coders@gmail.com>
Date:   Thu Jul 20 09:39:48 2011 +0200

    Add README.md
    
    Installation instructions""")
        self.assertEqual([
            {
            'Commit': 'f2d2cc3b4e84104b5ca4cae16a07f8b924d2bb06',
            'Author': 'David Siñuela Pastor <siu.4coders@gmail.com>',
            'Date': datetime.datetime(2011, 7, 21, 9, 39, 48),
            'Title': 'Don\'t commit in test_add_all integration test',
            'Message': 'Don\'t commit in test_add_all integration test\nNot needed'
            },
            {
            'Commit': '018825f04b0f58f3f9b852da3e21f9e84441d657',
            'Author': 'David Siñuela Pastor <siu.4coders@gmail.com>',
            'Date': datetime.datetime(2011, 7, 20, 9, 39, 48),
            'Title': 'Add README.md',
            'Message': 'Add README.md\n\nInstallation instructions'
            }], self.repo.log)
        self.git_cmd.assert_called_with(
                '--git-dir=".git" log --format=medium',
                self.repo.path)


class GitRepoExternalGitDirTest(GitRepoBaseTest):
    def setUp(self):
        self.repo = git_repo.GitRepo('bogus_repo', '../bogus_repo.git')

    def test_paths_different_git_dir(self):
        self.mock_git_cmd("sample_file.txt\ntest/test_a.py\n")

        assert self.repo.paths

        self.git_cmd.assert_called_with('--git-dir="../bogus_repo.git" ls-files', 
                self.repo.path)
