"""
Install upstart init services definition with initctl command

http://upstart.ubuntu.com/

"""

import logging
from os import path
import os
from subprocess import check_call, check_output, CalledProcessError, PIPE
import sys

from chalmers.service.cron_service import CronService
import platform


python_exe = sys.executable
chalmers_script = sys.argv[0]

log = logging.getLogger(__name__)

UPSTART_INIT_DIR = '/etc/init'

def read_data(filename):
    filename = path.join(path.dirname(__file__), 'data', filename)
    with open(filename) as fd:
        return fd.read()

def check():
    try:
        check_call(['initctl', '--version'], stdout=PIPE)
        return True
    except OSError as err:
        if err.errno == 2:
            return False
        raise

class UpstartService(object):
    __new__ = CronService.use_if_not_root

    def __init__(self, target_user):
        self.target_user = target_user

        log.info('Platform: %s' % (platform.linux_distribution()[0] or 'Unknown'))
        log.info('Using Linux upstart')
        if target_user:
            log.info('Chalmers service for target user' % target_user)
        else:
            log.info('Chalmers service for root user')

    @property
    def script_name(self):
        if self.target_user:
            return 'chalmers.%s' % self.target_user
        else:  # Run as root
            return 'chalmers'
    @property
    def script_path(self):
        return path.join(UPSTART_INIT_DIR, '%s.conf' % self.script_name)

    @property
    def launch_command(self):
        if self.target_user:
            return '/bin/su - %s' % self.target_user
        else:  # Run as root
            return '/bin/sh'

    def install(self):

        data = read_data('upstart.conf').format(python_exe=python_exe,
                                                chalmers=chalmers_script,
                                                launch=self.launch_command)

        with open(self.script_path, 'w') as fd:
            fd.write(data)

        log.info('Write file: %s' % self.script_path)

    def uninstall(self):
        if path.exists(self.script_path):
            log.info('Remove file: %s' % self.script_path)
            os.unlink(self.script_path)
            log.info("Chalmers service has been removed")
        else:
            log.info("Chalmers service does not exist")

    def status(self):
        #     initctl status chalmers

        command = ['initctl', 'status', self.script_name]
        log.info('Running command: %s' % ' '.join(command))
        try:
            output = check_output(command)
            log.info(output)
        except CalledProcessError as err:
            if err.returncode == 1:
                log.info("Chalmers will not start on boot")
                return False
            raise

        if not path.exists(self.script_path):
            log.warn("Service file '%s' does not exist " % self.script_path)

        log.info("Chalmers is setup to start on boot")

        return True
