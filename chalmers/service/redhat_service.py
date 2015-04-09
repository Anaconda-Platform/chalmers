"""
"""
from __future__ import unicode_literals, print_function

import logging
from os import path
import os
from subprocess import check_call, check_output, CalledProcessError, PIPE
import sys

log = logging.getLogger('chalmers.service')

INIT_D_DIR = '/etc/init.d'

python_exe = sys.executable
chalmers_script = sys.argv[0]

def read_data(filename):
    filename = path.join(path.dirname(__file__), 'data', filename)
    with open(filename) as fd:
        return fd.read()

def have_chkconfig():
    try:
        check_call(['chkconfig'], stdout=PIPE)
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

    data = read_data('chalmers-chkconfig.sh').format(python_exe=python_exe,
                                                     chalmers=chalmers_script,
                                                     launch=launch,
                                                     script_name=script_name)


    filepath = path.join(INIT_D_DIR, script_name)

    with open(filepath, 'w') as fd:
        fd.write(data)
    log.info('Write file: %s' % filepath)
    os.chmod(filepath, 0754)
    log.info('Running command chmod 754 %s' % filepath)

    command = ['chkconfig', script_name, 'on']
    log.info('Running command: %s' % ' '.join(command))
    output = check_output(command)
    log.info(output)



def uninstall(target_user):

    if target_user:
        script_name = 'chalmers.%s' % target_user
    else:  # Run as root
        script_name = 'chalmers'

    command = ['chkconfig', '--del', script_name]
    log.info('Running command: %s' % ' '.join(command))
    try:
        output = check_output(command)
        log.info(output)
    except CalledProcessError as err:
        if err.returncode == 1:
            log.info("chkconfig is not installed")
        else: raise
    filepath = path.join(INIT_D_DIR, script_name)
    if not path.exists(filepath):
        log.warn("File '%s' does not exist " % filepath)
    else:
        os.unlink(filepath)
    log.info("Chalmers service has been removed")

def status(target_user):

    if target_user:
        script_name = 'chalmers.%s' % target_user
    else:  # Run as root
        script_name = 'chalmers'

    command = ['chkconfig', '--list', script_name]
    log.info('Running command: %s' % ' '.join(command))
    try:
        output = check_output(command)
        log.info(output)
    except CalledProcessError as err:
        if err.returncode == 1:
            log.info("Chalmers will not start on boot")
            return False
        raise


    filepath = path.join(INIT_D_DIR, script_name)
    if not path.exists(filepath):
        log.warn("Service file '%s' does not exist " % filepath)
    log.info("Chalmers is setup to start on boot")
    return True



