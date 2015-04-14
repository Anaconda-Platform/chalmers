"""
Install a crontab rule to run at system boot

E.g.::
    
    @reboot /path/to/python /path/to/chalmers start -a
    
FIXME: There may be cases where the reboot command does not work 
correctly.
 
 * http://unix.stackexchange.com/questions/109804/crontabs-reboot-only-works-for-root
 
"""
from __future__ import unicode_literals, print_function

import logging
import subprocess as sp
import sys

from chalmers import errors
import os
import platform


python_exe = sys.executable
chalmers_script = sys.argv[0]
chalmers_tab_entry = '@reboot %s %s start -a' % (python_exe, chalmers_script)

log = logging.getLogger('chalmers.reboot')

def check():
    try:
        sp.check_output(['crontab', '-l'], stderr=sp.STDOUT)
    except sp.CalledProcessError as err:
        if err.returncode == 1 and 'crontab: no crontab for' in err.output:
            return True
        raise
    except IOError as err:
        if err.errno == 2: return False
        raise
    else:
        return True

def get_crontab():
    try:
        output = sp.check_output(['crontab', '-l']).strip()
    except sp.CalledProcessError as err:
        if err.returncode != 1:
            raise errors.ChalmersError("Could not read crontab")
        return []

    return output.split('\n')

def set_crontab(tab):
    new_cron_tab = '\n'.join(tab) + '\n'

    p0 = sp.Popen(['crontab'], stdin=sp.PIPE)
    p0.communicate(input=new_cron_tab)

py3 = sys.version_info.major == 3
class CronService(object):
    """
    Install a @reboot insruction to the user's local cron table
    """

    def __init__(self, target_user):
        if target_user is not False:
            msg = ("Not implemented: chalmers can not detect "
                   "the init system for your unix machine "
                   "(upstart, systemd or sysv)")
            raise errors.ChalmersError(msg)
        self.target_user = target_user
        log = logging.getLogger('chalmers.cron_service')

        log.info('Platform: %s' % platform.linux_distribution()[0] or 'Unknown')
        log.info('Using posix crond @reboot command')
        log.info('Chalmers service for current user (does not require root)')


    @classmethod
    def use_if_not_root(cls, subcls, target_user):
        if target_user is False:
            if py3:
                return object.__new__(cls)
            else:
                return object.__new__(cls, target_user)

        else:
            if os.getuid() != 0:
                raise errors.ChalmersError("You can not install a posix service for "
                                           "user %s without root privileges. "
                                           "Run this command again with sudo")
            if py3:
                return object.__new__(subcls)
            else:
                return object.__new__(subcls, target_user)

    def install(self):
        tab_lines = get_crontab()

        if chalmers_tab_entry in tab_lines:
            log.warn("Chalmers crontab instruction already exists")
            return True
        else:
            log.info("Adding chalmers instruction to crontab")
            tab_lines.append(chalmers_tab_entry)

            set_crontab(tab_lines)

            log.info("All chalmers programs will now run on boot")
            return True


    def uninstall(self):

        tab_lines = get_crontab()
        if chalmers_tab_entry in tab_lines:
            log.info("Removing chalmers instruction from crontab")
            tab_lines.remove(chalmers_tab_entry)

            set_crontab(tab_lines)
            return True

        else:
            log.info("Chalmers crontab instruction does not exist")
            return False

    def status(self):

        tab_lines = get_crontab()

        if chalmers_tab_entry in tab_lines:
            log.info("Chalmers is setup to start on boot")
            return True
        else:
            log.info("Chalmers will not start on boot")
            return False

