'''
'''
from __future__ import unicode_literals, print_function

import logging

from chalmers.program import Program
from chalmers import errors
from datetime import timedelta
import time
import getpass
import os
log = logging.getLogger(__name__)

def windows_main(args):


    from chalmers.windows.install import instart
    from chalmers.windows.chalmers_service import ChalmersService

    from win32com.shell import shell
    if not shell.IsUserAnAdmin():
        raise erros.ChalmersError("The current user is not an admin")
    
    password = getpass.getpass(b"Password for %s: " % args.username)
    
    instart('.\\%s' % args.username, password)

def windows_main_uninstall(args):
    from win32serviceutil import RemoveService, StopService
    from chalmers.windows.install import get_service_name, is_installed, is_running
    
    service_name = get_service_name(args.username)

    if is_running(args.username):
        log.info("Service is running, stopping service %s" % service_name)
        StopService(service_name)
    
    if is_installed(args.username):
        RemoveService(service_name)
        log.info("Uninstalled windows service '%s'" % service_name)
    else:
        log.error("Windows service '%s' is not insatlled" % service_name)

def windows_main_status(args):
    from chalmers.windows.install import get_service_name, is_installed, is_running
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
    from chalmers.event_handler import send_action    
    pid = send_action("chalmers", "ping")
    log.info("Chalmers manger pid is %s" % pid)

if os.name =='nt':
    main = windows_main
    main_unintall = windows_main_uninstall
    main_status = windows_main_status

def add_parser(subparsers):
    parser = subparsers.add_parser('install-service',
                                      help='Install chalmers as a service',
                                      description=__doc__)
    parser.add_argument('-u','--username', default=getpass.getuser(),
                        help='User account to run chalmers in (default: %(default)s)')
    parser.set_defaults(main=main)

    #####  #####  #####  #####  #####  #####  #####  #####  #####  #####  
    #####  #####  #####  #####  #####  #####  #####  #####  #####  #####  
    parser = subparsers.add_parser('uninstall-service',
                                      help='Uninstall chalmers as a service',
                                      description=__doc__)
    parser.add_argument('-u','--username', default=getpass.getuser(),
                        help='User account to run chalmers in (default: %(default)s)')
    parser.set_defaults(main=main_unintall)
    #####  #####  #####  #####  #####  #####  #####  #####  #####  #####  
    #####  #####  #####  #####  #####  #####  #####  #####  #####  #####  
    parser = subparsers.add_parser('service-status',
                                      help='Check the status of the service',
                                      description=__doc__)
    parser.add_argument('-u','--username', default=getpass.getuser(),
                        help='User account to run chalmers in (default: %(default)s)')

    parser.set_defaults(main=main_status)
