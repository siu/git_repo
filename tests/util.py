import os
import shutil
import tarfile
import tempfile
import unittest

from git_wrapper import GitWrapper

def open_repo(repo_dir, git_dir = '.git'):
    repo_path = os.path.join(os.path.dirname(__file__), 'fixtures', repo_dir)
    temp_dir = tempfile.mkdtemp()
    temp_repo_path = os.path.join(temp_dir, repo_dir)
    shutil.copytree(repo_path, temp_repo_path)
    return temp_dir, GitWrapper(temp_repo_path, git_dir)

class RepoTestCase(unittest.TestCase):
    def tearDown(self):
        shutil.rmtree(self._temp_dir)

    def open_tar_repo(self, repo_dir, git_dir = '.git'):
        repo_path = os.path.join(os.path.dirname(__file__), 'fixtures',
                repo_dir)
        temp_dir = tempfile.mkdtemp()
        tar = tarfile.open(repo_path + '.tar')
        tar.extractall(temp_dir)
        tar.close()

        self._temp_dir = temp_dir
        self.repo = GitWrapper(repo_path, git_dir)

