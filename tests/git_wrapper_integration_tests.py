import unittest
import util
from git_wrapper import GitWrapper

class GitWrapperIntegrationTest(util.RepoTestCase):
    def test_paths(self):
        self.open_tar_repo('project01')
        assert('test_file.txt' in self.repo.paths)
        assert('hello_world.rb' in self.repo.paths)

    def test_stage(self):
        self.open_tar_repo('project02')
        assert('not_committed_file.txt' in self.repo.stage)
        assert('second_not_committed_file.txt' in self.repo.stage)

    def test_paths_external_git_folder(self):
        self.open_tar_repo('project03', '../project03.git')
        assert('test_file.txt' in self.repo.paths)
        assert('hello_world.rb' in self.repo.paths)

    def test_stage_external_git_folder(self):
        self.open_tar_repo('project04', '../project04.git')
        assert('not_committed_file.txt' in self.repo.stage)
        assert('second_not_committed_file.txt' in self.repo.stage)
