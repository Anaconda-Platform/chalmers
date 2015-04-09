"""
Install windows services
"""
from __future__ import print_function, absolute_import, unicode_literals
import getpass
import logging
from os import path
import os

from chalmers import errors
from chalmers.event_dispatcher import send_action
from chalmers.program_manager import ProgramManager
from chalmers.windows.install import get_service_name, is_installed, is_running
from chalmers.windows.install import instart
from win32com.shell import shell
from win32serviceutil import RemoveService, StopService
from win32api import GetUserName
import sys



log = logging.getLogger(__name__)

HOME = os.environ.get('HOMEPATH')
STARTUP_DIR = path.join(HOME, 'AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup')


def local_install():
    filepath = path.join(STARTUP_DIR, 'chalmers.bat')

    chalmers_script = sys.argv[0]
    command = [sys.executable, chalmers_script, 'start', '--all']

    with open(filepath, 'w') as fd:
        log.info("Write file: %s" % filepath)
        print(' '.join(command), file=fd)

    log.info("All chalmers programs will now run on login")



def local_uninstall():

    filepath = path.join(STARTUP_DIR, 'chalmers.bat')

    if os.path.exists(filepath):
        log.info("Remvoe File: %s" % filepath)
        os.unlink(filepath)
    else:
        log.warning("File: %s does not exst" % filepath)

    log.info("Chalmers local service has been removed")


def local_status():
    filepath = path.join(STARTUP_DIR, 'chalmers.bat')
    if os.path.exists(filepath):
        log.info("Chalmers is setup to start on boot")
    else:
        log.info("Chalmers will not start on boot")

def system_install(target_user):
    if not shell.IsUserAnAdmin():
        raise errors.ChalmersError("System services requires admin privleges. "
                                   "run this command as an administrator")

    log.info("Your password is required by the windows service manager to launch"
             "The chalmers service at login")
    password = getpass.getpass(b"Password for %s: " % target_user)

    instart('.\\%s' % target_user, password)


def system_uninstall(target_user):
    if not shell.IsUserAnAdmin():
        raise errors.ChalmersError("System services requires admin privileges. "
                                   "run this command as an administrator")

    service_name = get_service_name(target_user)

    if is_running(target_user):
        log.info("Service is running, stopping service %s" % service_name)
        StopService(service_name)

    if is_installed(target_user):
        RemoveService(service_name)
        log.info("Uninstalled windows service '%s'" % service_name)
    else:
        log.error("Windows service '%s' is not installed" % service_name)

def system_status(target_user):

    service_name = get_service_name(target_user)

    log.info("Status for service '%s'" % service_name)

    if is_installed(target_user):
        log.info("service '%s' is installed" % service_name)
    else:
        log.error("service '%s' is not installed" % service_name)
        return

    if is_running(target_user):
        log.info("service '%s' is running" % service_name)
    else:
        log.error("service '%s' is not running" % service_name)
        return

    pid = send_action(ProgramManager.NAME, "ping")
    log.info("Chalmers manger pid is %s" % pid)

def install(args):

    if args.system is False:
        local_install()
    else:
        system_install(args.system or GetUserName())

def uninstall(args):

    if args.system is False:
        local_uninstall()
    else:
        system_uninstall(args.system or GetUserName())

def status(args):

    if args.system is False:
        local_status()
    else:
        system_status(args.system or GetUserName())

