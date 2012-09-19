#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Dead-simple git repository wrapper for Python

Copyright (c) 2011, David Siñuela Pastor

License: MIT (see LICENSE.txt for details)
"""
__author__ = 'David Siñuela Pastor'
__license__ = 'MIT'
__url__ = 'https://github.com/siu/git_repo'

import os
import subprocess
import shlex
import re
import datetime
import email.utils
from StringIO import StringIO

GIT_EXE = '/usr/bin/git'

class GitRepo(object):
    def __init__(self, path, git_dir='.git', branch_flag='--all'):
        self.path = os.path.abspath(path)
        self.git_dir = os.path.abspath(os.path.join(self.path, git_dir))
        self.branch_flag = branch_flag
        self.env = dict()
        self.env['GIT_DIR'] = self.git_dir
        self.env['GIT_WORK_TREE'] = self.path

    @classmethod
    def init(cls, path, git_dir='.git'):
        """Initialize a git repository, optionally with a separate git dir"""
        path = os.path.abspath(path)
        command = 'init "%s"' % path
        if git_dir != '.git':
            abs_git_dir = os.path.abspath(os.path.join(path, git_dir))
            command += ' --separate-git-dir=%s' % abs_git_dir

        output = GitRepo.execute_git_cmd(command)
        return GitRepo(path, git_dir)

    @property
    def paths(self):
        """List of files tracked by the repo"""
        output = self.git('ls-files')
        paths = output.split('\n')
        return paths

    @property
    def staging(self):
        """Contents of the staging area"""
        output = self.git('status --porcelain')
        paths = {}
        for line in output.split('\n'):
            line = line.strip()
            if line:
                status, filepath = line.split()
                paths[filepath] = status
        return paths

    @property
    def branches(self):
        """List of branches"""
        output = self.git('for-each-ref --format="%(refname:short)" refs/heads')
        branches = []
        for branch in output.split('\n'):
            branches.append(branch.strip())
        return branches


    def git(self, command):
        """Executes a command in the repository context"""
        cmd = '%s' % command
        return GitRepo.execute_git_cmd(cmd, cwd=self.path, env=self.env)

    def add(self, path):
        """git add(file)"""
        return self.git('add "%s"' % path)

    def add_all(self):
        """git add --all"""
        for file in self.staging.keys():
            self.add(file)

    def commit(self, message):
        """Commit staged changes with message"""
        return self.git('commit -m "%s"' % message)

    def log(self, limit=0, start=0):
        """returs a list of commits"""
        try:
            cmd = 'log --format=medium'
            if limit>0:
                cmd += ' -n %d' % limit
            if start>0:
                cmd += ' --skip=%d' % start
            cmd += ' %s' % self.branch_flag
            cmd_out = self.git(cmd)

            output = StringIO(cmd_out)

            return GitRepo.parse_log(output)
        except subprocess.CalledProcessError as e:
            print(e)
            return []

    def log_from_to(self, sha_from, sha_to):
        try:
            if sha_from is not None:
                range = '%s..%s' % (sha_to, sha_from)
            else:
                range = sha_to
            command = 'log --format=medium %s' % range
            cmd_out = self.git(command)
            output = StringIO(cmd_out)

            return GitRepo.parse_log(output)
        except subprocess.CalledProcessError as e:
            print(e)
            return []

    def date_of_commit(self, sha):
        """Returns a string in ISO 8601 format with the date of the commit"""
        try:
            command = 'log -s --format="%%ci" "%s"' % sha
            cmd_out = self.git(command)
            output = StringIO(cmd_out)

            return output.readline().strip()
        except subprocess.CalledProcessError as e:
            print(e)
            return ''

    def log_after_date(self, date):
        """Returns a list of commits from any branch ordered by date"""
        try:
            command = 'log --all --format=medium --after "%s"' % date
            cmd_out = self.git(command)
            output = StringIO(cmd_out)

            return GitRepo.parse_log(output)[:-1]
        except subprocess.CalledProcessError as e:
            print(e)
            return []

    @property
    def last_commit_sha(self):
        """sha of last commit"""
        try:
            cmd_out = self.git('log --format=oneline %s' % self.branch_flag)
            output = StringIO(cmd_out).getvalue()

            return output.split(' ')[0].strip()
        except subprocess.CalledProcessError as e:
            print(e)
            return ''

    def read_commit(self, commit_sha):
        """returns the contents of a commit"""
        return self.git("show %s" % commit_sha)

    def show(self, obj_ref):
        """returns the contents of a git object"""
        return self.git("show %s" % obj_ref)

    def last_commit_of(self, commit_sha, filepath):
        """returns the last commit for a specific file upto the specified commit"""
        out = self.git('log --format="%s" -n 1 %s -- %s' % ('%H;;;%ar;;;%an;;;%s', commit_sha, filepath))
        parts = out.split(';;;')
        return {'commit': parts[0],
                'date': parts[1],
                'author': parts[2],
                'message': parts[3].split('    ')[0].strip()}

    @staticmethod
    def parse_log(file):
        """parse the log output from a stream-like file"""
        commits = []
        current_commit = {}

        while True:

            line = file.readline()

            if len(line) == 0:
                break

            commit_match = re.match(r'^commit (\w*)', line)
            author_match = re.match(r'^Author:\s+(.*)', line)
            date_match = re.match(r'^Date:\s+(.*)', line)
            message_match = re.match(r'    (.*)', line)

            if commit_match:
                current_commit['commit'] = commit_match.group(1)
            elif author_match:
                current_commit['author'] = author_match.group(1)
            elif date_match:
                current_commit['date'] = GitRepo.parse_tz_time(date_match.group(1))
            elif message_match:
                current_commit['title'] = message_match.group(1)

                message_lines = []
                while message_match:
                    svn_match = re.match(r'    git-svn-id:.*@(\d+) .*', line)
                    if svn_match:
                        current_commit['revision'] = svn_match.group(1)
                    else:
                        message_lines.append(message_match.group(1))
                    line = file.readline()
                    message_match = re.match(r'    (.*)', line)

                current_commit['message'] = '\n'.join(message_lines)

                commits.append(current_commit)
                current_commit = {}

        return commits

    @staticmethod
    def touni(x, enc='utf-8', err='strict'):
        """convert x to utf-8"""
        try:
            return unicode(x, enc, err).encode('utf-8')
        except UnicodeDecodeError:
            return unicode(x, 'iso-8859-1', err).encode('utf-8')

    @staticmethod
    def execute_git_cmd(cmd, cwd='.', env=dict()):
        """Execute git shell command
        raises GitRepoException the return code is different than 0
        returns the output as string"""

        #print(cmd, env)

        command = [ GIT_EXE ]
        command.extend(shlex.split(cmd))
        cmd = subprocess.Popen(command, cwd=cwd, stdout=subprocess.PIPE,
                stderr=subprocess.PIPE)
        cmd.wait()
        output = cmd.stdout.read()
        output = GitRepo.touni(output)

        #print(cmd.returncode)

        if cmd.returncode != 0:
            raise GitRepoException(cmd.stderr.read())

        return output.strip()

    @staticmethod
    def parse_tz_time(text):
        return datetime.datetime.fromtimestamp(email.utils.mktime_tz(email.utils.parsedate_tz(text)))


class GitRepoException(Exception):
    pass

