"""
Install a crontab rule to run at system boot 
"""
from __future__ import unicode_literals, print_function

import logging
from os import path
import os
from subprocess import Popen, check_call, check_output, CalledProcessError, PIPE
import sys

from chalmers import errors

from . import cron_service, redhat_service


log = logging.getLogger('chalmers.service')

python_exe = sys.executable
chalmers_script = sys.argv[0]

def have_upstart():
    try:
        check_call(['initctl', '--version'], stdout=PIPE)
        return True
    except OSError as err:
        if err.errno == 2:
            return False
        raise


def system_install(target_user):
    if os.getuid() != 0:
        raise errors.ChalmersError("You must run chalmers as root when using the --system argument")

    if target_user is None:
        target_user = os.environ.get('SUDO_USER')

    if redhat_service.have_chkconfig():
        redhat_service.install(target_user)
    else:
        raise NotImplementedError("TODO:")

    log.info("All chalmers programs will now run on boot")

def system_uninstall(target_user):
    if os.getuid() != 0:
        raise errors.ChalmersError("You must run chalmers as root when using the --system argument")

    if target_user is None:
        target_user = os.environ.get('SUDO_USER')

    if redhat_service.have_chkconfig():
        redhat_service.uninstall(target_user)
    else:
        raise NotImplementedError("TODO:")

def system_status(target_user):

    if target_user is None:
        target_user = os.environ.get('SUDO_USER')

    if redhat_service.have_chkconfig():
        redhat_service.status(target_user)
    else:
        raise NotImplementedError("TODO:")


def install(args):

    if args.system is False:
        cron_service.install()
    else:
        system_install(args.system)

def uninstall(args):

    if args.system is False:
        cron_service.uninstall()
    else:
        system_uninstall(args.system)

def status(args):

    if args.system is False:
        cron_service.status()
    else:
        system_status(args.system)

