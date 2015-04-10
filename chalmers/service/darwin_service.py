"""
Install a launchd rule to run at boot

http://en.wikipedia.org/wiki/Launchd
 
"""
from __future__ import unicode_literals, print_function

import logging
import os
import pwd
from subprocess import CalledProcessError, check_output as _check_output, STDOUT
import sys

from chalmers import errors


launchd_label = "org.continuum.chalmers"

log = logging.getLogger('chalmers.service')

def demote(user_uid, user_gid):
    'pre exec function to drop root privleges on Popen'

    def result():
        os.setgid(user_gid)
        os.setuid(user_uid)

    return result


class DarwinService(object):
    def __init__(self, target_user):
        self.target_user = target_user

    @property
    def label(self):
        if self.target_user:
            return '%s.%s' % (launchd_label, self.target_user)
        else:
            return launchd_label

    def check_output(self, command):
        if self.target_user:
            pw = pwd.getpwnam(self.target_user)
            env = os.environ.copy()
            env.update({'HOME': pw.pw_dir, 'SHELL': pw.pw_shell, 'USER': pw.pw_name})
            preexec_fn = demote(pw.pw_uid, pw.pw_gid)
            log.info("Changing USER/UID/GID to: %s/%s/%s" % (pw.pw_name, pw.pw_uid, pw.pw_gid))
        else:
            env = os.environ
            preexec_fn = None

        log.info("Running command: %s" % ' '.join(command))
        try:
            output = _check_output(command, env=env, cwd='/', preexec_fn=preexec_fn, stderr=STDOUT)
        except OSError as err:
            raise errors.ChalmersError("Could not access program 'launchctl' required for osx service install")
        except CalledProcessError as err:
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
        except CalledProcessError as err:
            if err.returncode == 1:
                return None
            raise

    def add_launchd(self):

        try:
            chalmers_script = sys.argv[0]
            command = ['launchctl', 'submit', '-l', self.label, '--',
                       sys.executable, chalmers_script, 'start', '--all']
            self.check_output(command).strip()
        except CalledProcessError as err:
            if err.returncode == 1:
                raise errors.ChalmersError("Chalmers service is already installed")
            raise


    def install(self):
        """Create a launchd plist and load as a global daemon"""

        log.info("Adding chalmers launchd plist")
        self.add_launchd()
        log.info("All chalmers programs will now run on boot")

    def uninstall(self):
        """Uninstall launchd plist for chalmers"""

        log.info("Removing chalmers plist from launchd")
        try:
            command = ['launchctl', 'remove', self.label]
            self.check_output(command).strip()
        except CalledProcessError as err:
            if err.returncode == 1:
                raise errors.ChalmersError("Chalmers service is not installed")
            raise

        log.info("Chalmers service has been removed")

    def status(self):
        """Check if chalmers will be started at reboot"""

        launchd_lines = self.get_launchd()
        if launchd_lines:
            log.info("Chalmers is setup to start on boot")
        else:
            log.info("Chalmers will not start on boot")

