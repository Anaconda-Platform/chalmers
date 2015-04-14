"""
Install "SysV-style" init services definition with chkconfig command

http://en.wikipedia.org/wiki/Init

Note: chkconfig only soft links the /etc/inid.d/ script to the proper /etc/rc files. 
We could check if this could be done manually. chkconfig behaves strange on some systems.  
"""

from __future__ import unicode_literals, print_function

import logging
from os import path
import os
from subprocess import check_call, CalledProcessError, PIPE, check_output as _check_output
import sys

from chalmers.service.cron_service import CronService
import platform


log = logging.getLogger('chalmers.service')

INIT_D_DIR = '/etc/init.d'
python_exe = sys.executable
chalmers_script = sys.argv[0]

def read_data(filename):
    filename = path.join(path.dirname(__file__), 'data', filename)
    with open(filename) as fd:
        return fd.read()

def check():
    try:
        check_call(['chkconfig'], stdout=PIPE)
        return True
    except OSError as err:
        if err.errno == 2:
            return False
        raise

class SysVService(object):
    # Returns CronService if user is not root
    __new__ = CronService.use_if_not_root

    def __init__(self, target_user):
        self.target_user = target_user

        log.info('Platform: %s' % (platform.linux_distribution()[0] or 'Unknown'))
        log.info('Using Linux sysv chkconfig')
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
        return path.join(INIT_D_DIR, self.script_name)

    @property
    def launch(self):
        if self.target_user:
            return '/bin/su - %s' % self.target_user
        else:  # Run as root
            return '/bin/sh'

    def check_output(self, command):
        log.info('Running command: %s' % ' '.join(command))
        output = _check_output(command)
        log.info(output)
        return output


    @property
    def template(self):
        return read_data('sysv-init.sh')


    def install(self):

        data = self.template.format(python_exe=python_exe,
                           chalmers=chalmers_script,
                           launch=self.launch,
                           script_name=self.script_name)


        with open(self.script_path, 'w') as fd:
            fd.write(data)

        log.info('Write file: %s' % self.script_path)
        os.chmod(self.script_path, 0754)
        log.info('Running command chmod 754 %s' % self.script_path)

        # Redhat, CentOS
        self.check_output(['chkconfig', self.script_name, 'on'])


    def uninstall(self):
        self.check_output(['chkconfig', '--del', self.script_name])


        if not path.exists(self.script_path):
            log.warn("File '%s' does not exist " % self.script_path)
        else:
            os.unlink(self.script_path)

        log.info("Chalmers service has been removed")

    def status(self):

        try:
            self.check_output(['chkconfig', '--list', self.script_name])
        except CalledProcessError as err:
            if err.returncode == 1:
                log.info("Chalmers will not start on boot")
                return False
            raise


        if not path.exists(self.script_path):
            log.warn("Service file '%s' does not exist " % self.script_path)
        log.info("Chalmers is setup to start on boot")
        return True



