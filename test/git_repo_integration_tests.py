# -*- coding: utf-8 -*-

import os
import shutil
import unittest

import datetime

import util
import git_repo

class GitRepoIntegrationTest(util.RepoTestCase):
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
        self.repo = git_repo.GitRepo.init('new_project')
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
            {   'Author': 'David Siñuela Pastor <siu.4coders@gmail.com>',
                'Commit': '15fdec753d97d45240ce724c51b06f196d9fc879',
                'Date': datetime.datetime(2011, 7, 19, 0, 11, 52),
                'Title': 'Add sample_file.txt',
                'Message': 'Add sample_file.txt'
            }],
            self.repo.log)


class GitRepoIntegrationTestExternalGitFolder(util.RepoTestCase):
    def test_paths_external(self):
        self.open_tar_repo('project03', '../project03.git')
        self.assertEqualSet(self.repo.paths, 
            ['test_file.txt', 'hello_world.rb'])

    def test_staging_external(self):
        self.open_tar_repo('project04', '../project04.git')
        self.assertEqual(self.repo.staging, {
            'not_committed_file.txt': '??', 
            'second_not_committed_file.txt': '??'
            })

    def test_init(self):
        self.repo = git_repo.GitRepo.init('new_project', 'new_project.git')
        self._temp_dir = self.repo.path
        assert os.path.exists('new_project.git')
        shutil.rmtree('new_project.git')

