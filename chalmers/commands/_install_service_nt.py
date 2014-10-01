"""
Install windows services
"""
import getpass
import logging

from chalmers import errors
from chalmers.event_dispatcher import send_action
from chalmers.windows.install import get_service_name, is_installed, is_running
from chalmers.windows.install import instart
from win32com.shell import shell
from win32serviceutil import RemoveService, StopService


log = logging.getLogger(__name__)

def main(args):

    if not shell.IsUserAnAdmin():
        raise errors.ChalmersError("The current user is not an admin")

    password = getpass.getpass(b"Password for %s: " % args.username)

    instart('.\\%s' % args.username, password)

def main_uninstall(args):

    service_name = get_service_name(args.username)

    if is_running(args.username):
        log.info("Service is running, stopping service %s" % service_name)
        StopService(service_name)

    if is_installed(args.username):
        RemoveService(service_name)
        log.info("Uninstalled windows service '%s'" % service_name)
    else:
        log.error("Windows service '%s' is not insatlled" % service_name)

def main_status(args):

    service_name = get_service_name(args.username)

    log.info("Status for service '%s'" % service_name)

    if is_installed(args.username):
        log.info("service '%s' is installed" % service_name)
    else:
        log.error("service '%s' is not installed" % service_name)
        return

    if is_running(args.username):
        log.info("service '%s' is running" % service_name)
    else:
        log.error("service '%s' is not running" % service_name)
        return

    pid = send_action("chalmers", "ping")
    log.info("Chalmers manger pid is %s" % pid)
