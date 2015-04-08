"""
Install a crontab rule to run at system boot 
"""
from __future__ import unicode_literals, print_function

import logging
from subprocess import Popen, check_output, CalledProcessError, PIPE

from chalmers import errors
from . import cron_service

log = logging.getLogger('chalmers.service')


def system_install(target_user):
    raise NotImplementedError("TODO:")

def system_uninstall(target_user):
    raise NotImplementedError("TODO:")

def system_status(target_user):
    raise NotImplementedError("TODO:")


def install(args):

    if args.system is None:
        cron_service.install()
    else:
        system_install(args.system)

def uninstall(args):

    if args.system is None:
        cron_service.install()
    else:
        system_uninstall(args.system)

def main_status(args):

    if args.system is None:
        cron_service.install()
    else:
        system_status(args.system)

