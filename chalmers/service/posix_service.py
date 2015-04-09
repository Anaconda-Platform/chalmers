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

from . import cron_service


log = logging.getLogger('chalmers.service')

python_exe = sys.executable
chalmers_script = sys.argv[0]

def read_data(filename):
    filename = path.join(path.dirname(__file__), 'data', filename)
    with open(filename) as fd:
        return fd.read()

def have_chkconfig():
    try:
        check_call(['chkconfig'], stdout=PIPE)
        return True
    except OSError as err:
        if err.errno == 2:
            return False
        raise
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

    if have_chkconfig():
        read_data('chalmers-chkconfig.sh').format(python_exe=python_exe, chalmers=chalmers_script)
    else:
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

