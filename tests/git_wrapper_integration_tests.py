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
