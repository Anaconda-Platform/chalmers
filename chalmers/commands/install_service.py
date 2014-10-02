'''
[Un]Install chalmers so that it will run at system boot

This set is required on win32 platforms:

eg:
   
    chalmers install-service
    
'''
from __future__ import unicode_literals, print_function
import getpass
import os
from argparse import RawDescriptionHelpFormatter

if os.name == 'nt':
    from . import _install_service_nt as svs
else:
    from . import _install_service_posix as svs


def add_parser(subparsers):
    parser = subparsers.add_parser('install-service',
                                      help='Install chalmers as a service',
                                      description=__doc__,
                                      formatter_class=RawDescriptionHelpFormatter)
    parser.add_argument('-u', '--username', default=getpass.getuser(),
                        help='User account to run chalmers in (default: %(default)s)')
    parser.add_argument('--wait', action='store_true')
    parser.set_defaults(main=svs.main)

    #####  #####  #####  #####  #####  #####  #####  #####  #####  #####
    #####  #####  #####  #####  #####  #####  #####  #####  #####  #####
    parser = subparsers.add_parser('uninstall-service',
                                      help='Uninstall chalmers as a service',
                                      description=__doc__,
                                      formatter_class=RawDescriptionHelpFormatter)
    parser.add_argument('-u', '--username', default=getpass.getuser(),
                        help='User account to run chalmers in (default: %(default)s)')
    parser.add_argument('--wait', action='store_true')

    parser.set_defaults(main=svs.main_uninstall)
    #####  #####  #####  #####  #####  #####  #####  #####  #####  #####
    #####  #####  #####  #####  #####  #####  #####  #####  #####  #####
    parser = subparsers.add_parser('service-status',
                                      help='Check the status of the service',
                                      description=__doc__,
                                      formatter_class=RawDescriptionHelpFormatter)
    parser.add_argument('-u', '--username', default=getpass.getuser(),
                        help='User account to run chalmers in (default: %(default)s)')

    parser.set_defaults(main=svs.main_status)
