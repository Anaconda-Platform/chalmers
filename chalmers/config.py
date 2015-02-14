from __future__ import unicode_literals, print_function

from chalmers.utils import appdirs
import os


dirs = appdirs.AppDirs('chalmers', 'srossross')

def set_relative_dirs(root):
    'Set the application directory relative root'
    global dirs
    dirs = appdirs.RelativeAppDirs(root)

def main_logfile():
    os.path.join(dirs.user_log_dir, 'chalmers.log')
