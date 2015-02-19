"""
Install windows services
"""
from contextlib import contextmanager
import getpass
import logging
from subprocess import Popen

from win32com.shell import shell
from win32serviceutil import RemoveService, StopService

from chalmers import errors
from chalmers.event_dispatcher import send_action
from chalmers.program_manager import ProgramManager
from chalmers.utils.cli import bool_input
from chalmers.windows.install import get_service_name, is_installed, is_running
from chalmers.windows.install import instart


log = logging.getLogger(__name__)

try:
    input = raw_input
except NameError:
    pass

def run_as_admin(args, cmd):


    if args.username and args.username.lower() != getpass.getuser().lower():
        raise errors.ChalmersError("Can not use --username option when not an admin")

    admin_user = "Administrator"
    log.warning("Manging windows services requires admin privleges")
    if not bool_input("would you like to run this command as user '%s'" % admin_user):
        log.error("Exiting")
        return

    cmd = ["runas", "/noprofile", "/env", "/user:%s" % admin_user,
          cmd]

    p0 = Popen(cmd)
    if p0.wait():
        raise errors.ChalmersError("Command 'runas' did not complete successfully")


@contextmanager
def wait_for_input(args):

    wait = args.wait
    msg = "Press enter to continue"
    try:
        yield
    except:
        log.exception('Error')
        if wait: input(msg)
        raise SystemExit(1)
    else:
        if wait: input(msg)



def main(args):
    with wait_for_input(args):
        if not shell.IsUserAnAdmin():
            run_as_admin(args, "chalmers install-service --wait --username %s" % getpass.getuser())
            return

        log.info("Your password is required by the windows service manager to launch"
                 "The chalmers service at login")
        password = getpass.getpass(b"Password for %s: " % args.username)

        instart('.\\%s' % args.username, password)

def main_uninstall(args):
    with wait_for_input(args):
        if not shell.IsUserAnAdmin():
            run_as_admin(args, "chalmers uninstall-service --wait --username %s" % getpass.getuser())
            return

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

    pid = send_action(ProgramManager.NAME, "ping")
    log.info("Chalmers manger pid is %s" % pid)
