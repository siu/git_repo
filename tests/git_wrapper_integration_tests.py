import unittest
from git_wrapper import GitWrapper

class GitWrapperIntegrationTest(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_paths(self):
        git_project = GitWrapper('tests/fixtures/fixture_project01',
                '../fixture_project01.git')
        assert('test_file.txt' in git_project.paths)
        assert('hello_world.rb' in git_project.paths)

    def test_stage(self):
        git_project = GitWrapper('tests/fixtures/fixture_project02',
        '../fixture_project02.git')
        assert('not_committed_file.txt' in git_project.stage)
        assert('second_not_committed_file.txt' in git_project.stage)
