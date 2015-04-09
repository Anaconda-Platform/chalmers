"""
"""

import logging
from os import path
import os
from subprocess import check_call, check_output, CalledProcessError, PIPE
import sys

python_exe = sys.executable
chalmers_script = sys.argv[0]

log = logging.getLogger(__name__)

def read_data(filename):
    filename = path.join(path.dirname(__file__), 'data', filename)
    with open(filename) as fd:
        return fd.read()

def have_initctl():
    try:
        check_call(['initctl', '--version'], stdout=PIPE)
        return True
    except OSError as err:
        if err.errno == 2:
            return False
        raise

def install(target_user):

    if target_user:
        script_name = 'chalmers.%s' % target_user
        launch = 'su - %s' % target_user
    else:  # Run as root
        launch = 'bash'
        script_name = 'chalmers'

    data = read_data('chalmers-upstart.conf').format(python_exe=python_exe,
                                                     chalmers=chalmers_script,
                                                     launch=launch)


    filepath = '/etc/init/%s.conf' % script_name
    with open(filepath, 'w') as fd:
        fd.write(data)
    log.info('Write file: %s' % filepath)

def uninstall(target_user):
    if target_user:
        script_name = 'chalmers.%s' % target_user
    else:  # Run as root
        script_name = 'chalmers'

    filepath = '/etc/init/%s.conf' % script_name
    if path.exists(filepath):
        log.info('Remove file: %s' % filepath)
        os.unlink(filepath)
        log.info("Chalmers service has been removed")
    else:
        log.info("Chalmers service does not exist")

def status(target_user):
#     initctl status chalmers
    if target_user:
        script_name = 'chalmers.%s' % target_user
    else:  # Run as root
        script_name = 'chalmers'

    command = ['initctl', 'status', script_name]
    log.info('Running command: %s' % ' '.join(command))
    try:
        output = check_output(command)
        log.info(output)
    except CalledProcessError as err:
        if err.returncode == 1:
            log.info("Chalmers will not start on boot")
            return False
        raise


    filepath = '/etc/init/%s.conf' % script_name
    if not path.exists(filepath):
        log.warn("Service file '%s' does not exist " % filepath)

    log.info("Chalmers is setup to start on boot")

    return True
