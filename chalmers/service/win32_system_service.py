"""
Install win32 system service. 

This requires admin privileges to run

 
"""

from __future__ import print_function, absolute_import, unicode_literals

import getpass
import logging

from win32api import GetUserName
from win32com.shell import shell
from win32serviceutil import RemoveService, StopService

from chalmers import errors
from chalmers.event_dispatcher import send_action
from chalmers.program_manager import ProgramManager
from chalmers.windows.install import get_service_name, is_installed, is_running
from chalmers.windows.install import instart


log = logging.getLogger(__name__)

class Win32SystemService(object):
    def __init__(self, target_user):
        if target_user is None:
            target_user = GetUserName()

        self.target_user = target_user

    @property
    def is_admin(self):
        return shell.IsUserAnAdmin()
    @property
    def service_name(self):
        return get_service_name(self.target_user)

    def install(self):
        if not self.is_admin:
            raise errors.ChalmersError("System services requires admin privleges. "
                                       "run this command as an administrator")

        log.info("Your password is required by the windows service manager to launch "
                 "the chalmers service at startup")
        password = getpass.getpass(b"Password for %s: " % self.target_user)

        instart('.\\%s' % self.target_user, password)


    def uninstall(self):
        if not self.is_admin:
            raise errors.ChalmersError("System services requires admin privileges. "
                                       "run this command as an administrator")

        if is_running(self.target_user):
            log.info("Service is running, stopping service %s" % self.service_name)
            StopService(self.service_name)

        if is_installed(self.target_user):
            RemoveService(self.service_name)
            log.info("Uninstalled windows service '%s'" % self.service_name)
        else:
            log.error("Windows service '%s' is not installed" % self.service_name)

    def status(self):

        log.info("Status for service '%s'" % self.service_name)

        if is_installed(self.target_user):
            log.info("service '%s' is installed" % self.service_name)
        else:
            log.error("service '%s' is not installed" % self.service_name)
            return

        if is_running(self.target_user):
            log.info("service '%s' is running" % self.service_name)
        else:
            log.error("service '%s' is not running" % self.service_name)
            return

        pid = send_action(ProgramManager.NAME, "ping")
        log.info("Chalmers manger pid is %s" % pid)


