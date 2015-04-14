"""
Install a launchd rule to run at boot

http://en.wikipedia.org/wiki/Launchd
 
"""
from __future__ import unicode_literals, print_function

import logging
from os import path
import os
import subprocess as sp
import sys

from chalmers import errors

import tempfile

python_exe = sys.executable
chalmers_script = sys.argv[0]


def read_data(filename):
    filename = path.join(path.dirname(__file__), 'data', filename)
    with open(filename) as fd:
        return fd.read()

launchd_label = "org.continuum.chalmers"

log = logging.getLogger('chalmers.service')

class DarwinService(object):
    def __init__(self, target_user):
        self.target_user = target_user

        log.info('Platform: Darwin')
        log.info('Using Darwin launchd service')

        if target_user:
            log.info('Launching chalmers as target user %s' % target_user)
        elif target_user is False:
            log.info('Launching chalmers as current user (does not require root)')
        else:
            log.info('Launching chalmers as root user')

    @property
    def label(self):
        if self.target_user:
            return '%s.%s' % (launchd_label, self.target_user)
        else:
            return launchd_label

    @property
    def template(self):
        return read_data('launchd.plist')

    def check_output(self, command):
        if self.target_user:
            if os.getuid() != 0:
                raise errors.ChalmersError("Can not perform system install without root")

        log.info("Running command: %s" % ' '.join(command))
        try:
            output = sp.check_output(command, stderr=sp.STDOUT)
        except OSError as err:
            raise errors.ChalmersError("Could not access program 'launchctl' required for osx service install")
        except sp.CalledProcessError as err:
            if err.returncode == 1:
                if 'Socket is not connected' in err.output:
                    log.error(err.output)
                    raise errors.ChalmersError("The user '%s' must be logged in via the osx gui to perform this operation" % self.target_user)
            raise

        return output

    def get_launchd(self):
        try:
            command = ['launchctl', 'list', self.label]
            return self.check_output(command)
        except sp.CalledProcessError as err:
            if err.returncode == 1:
                return None
            raise

    def add_launchd(self):
        if self.target_user:
            username = '<key>UserName</key> <string>%s</string>' % self.target_user
        else:
            username = ''
        plist = self.template.format(python_exe=python_exe,
                                     chalmers=chalmers_script,
                                     label=self.label,
                                     username=username)

        with tempfile.NamedTemporaryFile('w', suffix='.plist', prefix='chalmers') as fd:

            fd.write(plist)
            fd.flush()
            try:
                command = ['launchctl', 'load', fd.name]
                self.check_output(command).strip()
            except sp.CalledProcessError as err:
                if err.returncode == 1:
                    raise errors.ChalmersError("Chalmers service is already installed")
                raise


    def install(self):
        """Create a launchd plist and load as a global daemon"""

        log.info("Adding chalmers launchd plist")
        self.add_launchd()
        log.info("All chalmers programs will now run on boot")
        return True

    def uninstall(self):
        """Uninstall launchd plist for chalmers"""

        log.info("Removing chalmers plist from launchd")
        try:
            command = ['launchctl', 'remove', self.label]
            self.check_output(command).strip()
        except sp.CalledProcessError as err:
            if err.returncode == 1:
                log.error("Chalmers service is not installed")
                return False
            raise

        log.info("Chalmers service has been removed")
        return True

    def status(self):
        """Check if chalmers will be started at reboot"""
        launchd_lines = self.get_launchd()
        if launchd_lines:
            log.info("Chalmers is setup to start on boot")
            return True
        else:
            log.info("Chalmers will not start on boot")
            return False

