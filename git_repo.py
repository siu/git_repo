import os
import subprocess

GIT_EXE = '/usr/bin/git'

def execute_git_cmd(cmd, cwd='.'):
    command = [ GIT_EXE ]
    command.extend(cmd.split())
    output = subprocess.check_output(command, cwd=cwd)
    return output.strip()

class GitRepo(object):
    def __init__(self, path, git_dir='.git'):
        self.path = path
        self.git_dir = git_dir

    @classmethod
    def init(cls, path, git_dir = '.git'):
        command = 'init %s' % path
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
            status, filepath = line.strip().split()
            paths[filepath] = status
        return paths

    def git(self, command):
        cmd = "--git-dir=%s %s" % (self.git_dir, command)
        return execute_git_cmd(cmd, self.path)

    def add(self, path):
        return self.git('add %s' % path)

    def commit(self, message):
        return self.git('commit -m %s' % message)

