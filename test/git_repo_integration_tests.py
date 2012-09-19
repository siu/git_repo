# -*- coding: utf-8 -*-

import os
import unittest

import datetime
from git_repo import GitRepo

import util
import shutil
import tarfile
import tempfile

class RepoTestCase(util.BaseTestCase):
    def setUp(self):
        self._temp_dir = None

    def tearDown(self):
        if self._temp_dir:
            shutil.rmtree(self._temp_dir)

    def open_tar_repo(self, repo_dir, git_dir = '.git'):
        self._temp_dir = tempfile.mkdtemp()

        repo_tar = os.path.join(os.path.dirname(__file__), 'fixtures', repo_dir)
        tar = tarfile.open(repo_tar + '.tar')
        tar.extractall(self._temp_dir)
        tar.close()
        repo_path = os.path.join(self._temp_dir, repo_dir)

        self.repo = GitRepo(repo_path, git_dir=git_dir)

class GitRepoIntegrationTest(RepoTestCase):
    def test_paths(self):
        self.open_tar_repo('project01')
        self.assertEqualSet(self.repo.paths,
            ['test_file.txt', 'hello_world.rb'])

    def test_staging(self):
        self.open_tar_repo('project02')
        self.assertEqual(self.repo.staging, {
            'not_committed_file.txt': '??',
            'second_not_committed_file.txt': '??'
            })

    def test_staging_empty(self):
        self.open_tar_repo('project01')
        self.assertEqual(self.repo.staging, {})

    def test_add(self):
        self.open_tar_repo('project02')
        self.repo.add('not_committed_file.txt')
        self.assertEqual(self.repo.staging, {
            'not_committed_file.txt': 'A',
            'second_not_committed_file.txt': '??'
            })

    def test_commit(self):
        self.open_tar_repo('project02')
        self.repo.add('not_committed_file.txt')
        self.repo.commit('Add not_committed_file.txt to the repository')
        self.assertEqual(self.repo.staging, {
            'second_not_committed_file.txt': '??'
            })

    def test_commit_quotes_in_message(self):
        self.open_tar_repo('project02')
        self.repo.add('not_committed_file.txt')
        self.repo.commit('Add "not_committed_file.txt" to the repository')
        self.assertEqual(self.repo.staging, {
            'second_not_committed_file.txt': '??'
            })

    def test_init(self):
        self.repo = GitRepo.init('/tmp/new_project')
        self._temp_dir = self.repo.path
        assert os.path.exists(os.path.join(self.repo.path, '.git'))

    def test_add_all(self):
        self.open_tar_repo('project02')
        self.repo.add_all()
        self.assertEqual(self.repo.staging, {
            'not_committed_file.txt': 'A',
            'second_not_committed_file.txt': 'A'
            })

    def test_log(self):
        self.open_tar_repo('project02')
        self.assertEqual([
            {   'author': 'David Siñuela Pastor <siu.4coders@gmail.com>',
                'commit': '15fdec753d97d45240ce724c51b06f196d9fc879',
                'date': datetime.datetime(2011, 7, 19, 0, 11, 52),
                'title': 'Add sample_file.txt',
                'message': 'Add sample_file.txt'
            }],
            self.repo.log())


class GitRepoIntegrationTestExternalGitFolder(RepoTestCase):
    def test_paths_external(self):
        self.open_tar_repo('project03', '../project03.git')
        self.assertEqualSet(self.repo.paths,
            ['test_file.txt', 'hello_world.rb'])

    def test_staging_external(self):
        self.open_tar_repo('project04', '../project04.git')
        self._temp_dir = None
        self.assertEqual(self.repo.staging, {
            'not_committed_file.txt': '??',
            'second_not_committed_file.txt': '??'
            })

    def test_init(self):
        self.repo = GitRepo.init('/tmp/new_project', '/tmp/new_project.git')
        self._temp_dir = self.repo.path
        assert os.path.exists('/tmp/new_project.git')
        shutil.rmtree('/tmp/new_project.git')

