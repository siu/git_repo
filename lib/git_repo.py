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
        output = self.execute_git_cmd('ls-files')
        paths = output.split('\n')
        return paths

    @property
    def staging(self):
        output = self.execute_git_cmd('status --porcelain')
        paths = {}
        for line in output.split('\n'):
            status, filepath = line.strip().split()
            paths[filepath] = status
        return paths

    def execute_git_cmd(self, command):
        cmd = "--git-dir=%s %s" % (self.git_dir, command)
        return execute_git_cmd(cmd, self.path)

    def add(self, path):
        return self.execute_git_cmd('add %s' % path)

    def commit(self, message):
        return self.execute_git_cmd('commit -m %s' % message)
