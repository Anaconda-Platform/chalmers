"""
Install a crontab rule to run at system boot 
"""
from __future__ import unicode_literals, print_function

import logging
import os
from subprocess import Popen, check_output, CalledProcessError, PIPE

from chalmers import errors
from . import cron_service

log = logging.getLogger('chalmers.service')


def system_install(target_user):
    if os.getuid() != 0:
        raise errors.ChalmersError("You must run chalmers as root when using the --system argument")
    raise NotImplementedError("TODO:")

def system_uninstall(target_user):
    if os.getuid() != 0:
        raise errors.ChalmersError("You must run chalmers as root when using the --system argument")

    raise NotImplementedError("TODO:")

def system_status(target_user):
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

