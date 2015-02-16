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

# Set the root config and log dirs from an environment variable
if os.environ.get('CHALMERS_ROOT'):
    CHALMERS_ROOT = os.environ['CHALMERS_ROOT']
    set_relative_dirs(CHALMERS_ROOT)
