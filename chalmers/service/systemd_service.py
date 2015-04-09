"""
"""
from __future__ import unicode_literals, print_function

import logging
from os import path
import os
from subprocess import check_call, PIPE, check_output as _check_output, \
    CalledProcessError
import sys

from chalmers.service.cron_service import CronService


log = logging.getLogger('chalmers.service')

SYSTEM_D_INIT_DIR = '/etc/systemd/system'


python_exe = sys.executable
chalmers_script = sys.argv[0]

def read_data(filename):
    filename = path.join(path.dirname(__file__), 'data', filename)
    with open(filename) as fd:
        return fd.read()

def check():
    try:
        check_call(['systemctl', '--version'], stdout=PIPE)
        return True
    except OSError as err:
        if err.errno == 2:
            return False
        raise

class SystemdService(object):
    __new__ = CronService.use_if_not_root

    def __init__(self, target_user):
        self.target_user = target_user

    @property
    def script_name(self):
        if self.target_user:
            return 'chalmers.%s.service' % self.target_user
        else:  # Run as root
            return 'chalmers.service'
    @property
    def script_path(self):
        return path.join(SYSTEM_D_INIT_DIR, self.script_name)

    @property
    def launch_command(self):
        if self.target_user:
            return 'su - %s' % self.target_user
        else:  # Run as root
            return 'bash'

    @property
    def template(self):
        return read_data('systemd.service')

    def check_output(self, command):
        log.info('Running command: %s' % ' '.join(command))
        output = _check_output(command)
        log.info(output)
        return output

    def install(self):
        data = self.template.format(python_exe=python_exe,
                                    chalmers=chalmers_script,
                                    launch=self.launch_command)

        with open(self.script_path, 'w') as fd:
            print(data, file=fd)

        log.info("Wrote file: %s" % self.script_path)
        self.check_output(['systemctl', 'enable', self.script_name])

        log.info("Chalmers will now start on boot for user %s" % self.target_user)

    def uninstall(self):
        self.check_output(['systemctl', 'disable', self.script_name])

        if path.exists(self.script_path):
            os.unlink(self.script_path)
            log.info("Removed file: %s" % self.script_path)
        else:
            log.warning("Systemd service file %s does not exist" % self.script_path)

    def status(self):

        try:
            self.check_output(['systemctl', 'is-enabled', self.script_name])
        except CalledProcessError as err:
            if err.returncode == 1:
                log.info("Chalmers will not start on boot")
                return False
            raise
        if not path.exists(self.script_path):
            log.warn("Service file '%s' does not exist " % self.script_path)

        log.info("Chalmers is setup to start on boot for user %s" % self.target_user)
        return True



