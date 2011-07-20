import os
import shutil
import tarfile
import tempfile
import unittest

import git_repo

def open_repo(repo_dir, git_dir = '.git'):
    repo_path = os.path.join(os.path.dirname(__file__), 'fixtures', repo_dir)
    temp_dir = tempfile.mkdtemp()
    temp_repo_path = os.path.join(temp_dir, repo_dir)
    shutil.copytree(repo_path, temp_repo_path)
    return temp_dir, git_repo.GitRepo(temp_repo_path, git_dir)

class BaseTestCase(unittest.TestCase):
    def assertEqualSet(self, first, second):
        self.assertEqual(set(first), set(second))

class RepoTestCase(BaseTestCase):
    def tearDown(self):
        shutil.rmtree(self._temp_dir)

    def open_tar_repo(self, repo_dir, git_dir = '.git'):
        repo_tar = os.path.join(os.path.dirname(__file__), 'fixtures',
                repo_dir)
        temp_dir = tempfile.mkdtemp()
        tar = tarfile.open(repo_tar + '.tar')
        tar.extractall(temp_dir)
        tar.close()
        repo_path = os.path.join(temp_dir, repo_dir)

        self._temp_dir = temp_dir
        self.repo = git_repo.GitRepo(repo_path, git_dir)

