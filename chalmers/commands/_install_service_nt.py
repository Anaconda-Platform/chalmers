"""
Install windows services
"""
from __future__ import absolute_import, print_function
import os
import sys
import getpass
import logging
import getpass
from chalmers import errors
from chalmers.event_dispatcher import send_action
from chalmers.windows.install import get_service_name, is_installed, is_running
from chalmers.windows.install import instart
from win32com.shell import shell
from win32serviceutil import RemoveService, StopService
from chalmers.program_manager import ProgramManager
from subprocess import Popen, check_output, CalledProcessError, STDOUT
from chalmers.scripts import chalmers_main as main_script

log = logging.getLogger(__name__)

try:
    input = raw_input
except NameError:
    pass

def get_service_name():
    "Return the service name for the given user"
    svc_name = 'chalmers-manager-%s' % getpass.getuser()
    return svc_name


def is_installed():
    service_name = get_service_name()

    try:
        output = check_output(["schtasks", "/Query", "/TN", service_name], stderr=STDOUT)
        return True
    except CalledProcessError as err:
        if err.returncode != 1:
            raise
        expected_output = "ERROR: The system cannot find the file specified."
        if expected_output not in err.output:
            log.error("The program schtasks returned an unexpected output")
            log.error(err.output)
            log.error("Please contact a chalmers developer to investigate the issue")
    except WindowsError as err:
        if err.errno == 2:
            raise errors.ChalmersError("The system can not find the exe 'schtasks'")

        log.error("There was a fundamental error running the program schtasks")
        log.error("Please contact a chalmers developer to investigate the issue")
        raise

    return False

def main(args):
    service_name = get_service_name()

    if is_installed():
        log.error("Service %s is already installed" % service_name)
        return 


    script = os.path.abspath(main_script.__file__)

    if script.endswith('.pyc') or script.endswith('.pyo'):
        script = script[:-1]

    script_args = [sys.executable, script, 'start', '-a']
    cmd = ["schtasks", "/Create", "/SC", "ONSTART", "/TN", service_name, 
           "/TR", "'%s'" % "' '".join(script_args)]

    print("Running Windows command:")
    print('\t', ' '.join(cmd))
    check_output(cmd)

    print("service installed")

def main_uninstall(args):

    service_name = get_service_name()

    if not is_installed():
        log.error("Service %s is not installed" % service_name)
        return 

    cmd = ["schtasks", "/Delete", "/F", "/TN", service_name]

    print("Running Windows command:")
    print('\t', ' '.join(cmd))
    check_output(cmd)

    print("service removed")


def main_status(args):

    service_name = get_service_name()

    log.info("Status for service '%s'" % service_name)
    if is_installed():
        log.info("service '%s' is installed" % service_name)
    else:
        log.error("service '%s' is not installed" % service_name)
        return
