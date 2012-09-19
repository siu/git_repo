# -*- coding: utf-8 -*-

import util
import unittest
from mock import Mock

import re
import datetime

from git_repo import GitRepo

class GitRepoBaseTest(unittest.TestCase):
    def mock_git_cmd(self, return_value):
        self.git_cmd = Mock()
        self.git_cmd.return_value = return_value
        GitRepo.execute_git_cmd = self.git_cmd

    def assert_git_cmd(self, git_repo, command):
        args, kwargs = self.git_cmd.call_args
        self.assertEqual((command,), args)

        env = kwargs.get('env', None)
        if env is None:
            self.fail('env not set')

        self.assertEqual(git_repo.path, env.get('GIT_WORK_TREE', None))

        result_git_dir = env.get('GIT_DIR', None)
        if result_git_dir is None:
            self.fail('env[\'GIT_DIR\'] not set')

        regex = ".*%s$" % re.escape(git_repo.git_dir)
        self.assertRegexpMatches(result_git_dir, regex)

class GitRepoTest(GitRepoBaseTest):
    def setUp(self):
        self.maxDiff = None
        self.repo = GitRepo('bogus_repo')

    def test_paths(self):
        self.mock_git_cmd("sample_file.txt\ntest/test_a.py")

        self.assertEqual(self.repo.paths, ['sample_file.txt', 'test/test_a.py'])

        self.assert_git_cmd(self.repo, 'ls-files')

    def test_staging_new_files(self):
        self.mock_git_cmd("")

        self.assertEqual(self.repo.staging, {})

        self.assert_git_cmd(self.repo, 'status --porcelain')

    def test_staging_new_files(self):
        self.mock_git_cmd("?? sample_file.txt\n?? second_sample_file.txt")

        self.assertEqual(self.repo.staging, {
            'sample_file.txt': '??',
            'second_sample_file.txt': '??'
            })

        self.assert_git_cmd(self.repo, 'status --porcelain')

    def test_staging_modified_file(self):
        self.mock_git_cmd(" M sample_file.txt")

        self.assertEqual(self.repo.staging, { 'sample_file.txt': 'M' })

        self.assert_git_cmd(self.repo, 'status --porcelain')

    def test_commit_quotes_message(self):
        self.mock_git_cmd("")

        self.repo.commit('unquoted message')

        self.assert_git_cmd(self.repo, 'commit -m "unquoted message"')

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
            'commit': 'f2d2cc3b4e84104b5ca4cae16a07f8b924d2bb06',
            'author': 'David Siñuela Pastor <siu.4coders@gmail.com>',
            'date': datetime.datetime(2011, 7, 21, 9, 39, 48),
            'title': 'Don\'t commit in test_add_all integration test',
            'message': 'Don\'t commit in test_add_all integration test',
            },
            {
            'commit': '018825f04b0f58f3f9b852da3e21f9e84441d657',
            'author': 'David Siñuela Pastor <siu.4coders@gmail.com>',
            'date': datetime.datetime(2011, 7, 20, 9, 39, 48),
            'title': 'Add README.md',
            'message': 'Add README.md'
            }], self.repo.log())
        self.assert_git_cmd(self.repo, 'log --format=medium --all')

    def test_single_log(self):
        self.mock_git_cmd("""commit f2d2cc3b4e84104b5ca4cae16a07f8b924d2bb06
Author: David Siñuela Pastor <siu.4coders@gmail.com>
Date:   Thu Jul 21 09:39:48 2011 +0200

    Don't commit in test_add_all integration test""")
        self.assertEqual([
            {
            'commit': 'f2d2cc3b4e84104b5ca4cae16a07f8b924d2bb06',
            'author': 'David Siñuela Pastor <siu.4coders@gmail.com>',
            'date': datetime.datetime(2011, 7, 21, 9, 39, 48),
            'title': 'Don\'t commit in test_add_all integration test',
            'message': 'Don\'t commit in test_add_all integration test'
            }], self.repo.log())
        self.assert_git_cmd(self.repo, 'log --format=medium --all')

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
            'commit': 'f2d2cc3b4e84104b5ca4cae16a07f8b924d2bb06',
            'author': 'David Siñuela Pastor <siu.4coders@gmail.com>',
            'date': datetime.datetime(2011, 7, 21, 9, 39, 48),
            'title': 'Don\'t commit in test_add_all integration test',
            'message': 'Don\'t commit in test_add_all integration test\nNot needed'
            },
            {
            'commit': '018825f04b0f58f3f9b852da3e21f9e84441d657',
            'author': 'David Siñuela Pastor <siu.4coders@gmail.com>',
            'date': datetime.datetime(2011, 7, 20, 9, 39, 48),
            'title': 'Add README.md',
            'message': 'Add README.md\n\nInstallation instructions'
            }], self.repo.log())
        self.assert_git_cmd(self.repo, 'log --format=medium --all')


class GitRepoExternalGitDirTest(GitRepoBaseTest):
    def setUp(self):
        self.repo = GitRepo('bogus_repo', '../bogus_repo.git')

    def test_paths_different_git_dir(self):
        self.mock_git_cmd("sample_file.txt\ntest/test_a.py\n")

        assert self.repo.paths

        self.assert_git_cmd(self.repo, 'ls-files')

    def test_staging_different_git_dir(self):
        self.mock_git_cmd("?? sample_file.txt\n?? test/test_a.py\n")

        assert self.repo.staging

        self.assert_git_cmd(self.repo, 'status --porcelain')
