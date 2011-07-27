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
try:
    from cStringIO import StringIO
except:
    from StringIO import StringIO

GIT_EXE = '/usr/bin/git'

def execute_git_cmd(cmd, cwd='.'):
    command = [ GIT_EXE ]
    command.extend(shlex.split(cmd))
    output = subprocess.check_output(command, cwd=cwd)
    return output.strip()

class GitRepo(object):
    def __init__(self, path, git_dir='.git'):
        self.path = path
        self.git_dir = git_dir

    @classmethod
    def init(cls, path, git_dir = '.git'):
        command = 'init "%s"' % path
        if git_dir != '.git':
            command += ' --separate-git-dir=%s' % git_dir

        output = execute_git_cmd(command)
        return GitRepo(path, git_dir)

    @property
    def paths(self):
        output = self.git('ls-files')
        paths = output.split('\n')
        return paths

    @property
    def staging(self):
        output = self.git('status --porcelain')
        paths = {}
        for line in output.split('\n'):
            line = line.strip()
            if line:
                status, filepath = line.split()
                paths[filepath] = status
        return paths

    def git(self, command):
        cmd = '--git-dir="%s" %s' % (self.git_dir, command)
        return execute_git_cmd(cmd, self.path)

    def add(self, path):
        return self.git('add "%s"' % path)

    def add_all(self):
        for file in self.staging.keys():
            self.add(file)

    def commit(self, message):
        return self.git('commit -m "%s"' % message)

    @property
    def log(self):
        cmd_out = self.git('log --format=medium')
        output = StringIO(cmd_out)

        return get_log(output)


def get_log(file):
    commits = []
    current_commit = {}

    while True:

        line = file.readline()

        if len(line) == 0:
            break

        commit_match = re.match(r'^commit (\w*)', line)
        kw_match = re.match(r'^(\w+):\s+(.*)', line)
        message_match = re.match(r'    (.*)', line)

        if commit_match:
            current_commit['Commit'] = commit_match.group(1)
        elif kw_match:
            if kw_match.group(1) == 'Date':
                current_commit[kw_match.group(1)] = parse_tz_time(kw_match.group(2))
            else:
                current_commit[kw_match.group(1)] = kw_match.group(2)
        elif message_match:
            current_commit['Title'] = message_match.group(1)

            message_lines = []
            while message_match:
                message_lines.append(message_match.group(1))
                line = file.readline()
                message_match = re.match(r'    (.*)', line)

            current_commit['Message'] = '\n'.join(message_lines)

            commits.append(current_commit)
            current_commit = {}

    return commits

def parse_tz_time(text):
    return datetime.datetime.fromtimestamp(email.utils.mktime_tz(email.utils.parsedate_tz(text)))
        
