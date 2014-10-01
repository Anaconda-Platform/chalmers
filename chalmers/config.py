from __future__ import unicode_literals, print_function

from chalmers.utils import appdirs


dirs = appdirs.AppDirs('chalmers', 'srossross')

def set_relative_dirs(root):
    'Set the application directory relative root'
    global dirs
    dirs = appdirs.RelativeAppDirs(root)
