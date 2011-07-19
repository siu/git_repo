import os
import shutil
import unittest

import util
from git_wrapper import GitWrapper

class GitWrapperIntegrationTest(util.RepoTestCase):
    def test_paths(self):
        self.open_tar_repo('project01')
        self.assertEqualSet(self.repo.paths, 
            ['test_file.txt', 'hello_world.rb'])

    def test_stage(self):
        self.open_tar_repo('project02')
        self.assertEqual(self.repo.stage, {
            'not_committed_file.txt': '??', 
            'second_not_committed_file.txt': '??'
            })

    def test_add(self):
        self.open_tar_repo('project02')
        self.repo.add('not_committed_file.txt')
        self.assertEqual(self.repo.stage, {
            'not_committed_file.txt': 'A',
            'second_not_committed_file.txt': '??'
            })

    def test_commit(self):
        self.open_tar_repo('project02')
        self.repo.add('not_committed_file.txt')
        self.repo.commit('Add not_committed_file.txt')
        self.assertEqual(self.repo.stage, {
            'second_not_committed_file.txt': '??'
            })

    def test_init(self):
        self.repo = GitWrapper.init('new_project')
        self._temp_dir = self.repo.path
        assert os.path.exists(os.path.join(self.repo.path, '.git'))

class GitWrapperIntegrationTestExternalGitFolder(util.RepoTestCase):
    def test_paths_external(self):
        self.open_tar_repo('project03', '../project03.git')
        self.assertEqualSet(self.repo.paths, 
            ['test_file.txt', 'hello_world.rb'])

    def test_stage_external(self):
        self.open_tar_repo('project04', '../project04.git')
        self.assertEqual(self.repo.stage, {
            'not_committed_file.txt': '??', 
            'second_not_committed_file.txt': '??'
            })

    def test_init(self):
        self.repo = GitWrapper.init('new_project', 'new_project.git')
        self._temp_dir = self.repo.path
        assert os.path.exists('new_project.git')
        shutil.rmtree('new_project.git')

