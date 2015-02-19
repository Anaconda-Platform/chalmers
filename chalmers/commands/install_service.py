'''
[Un]Install chalmers so that it will run at system boot

This set is required on win32 platforms:

eg:
   
    chalmers service install
    
'''
from __future__ import unicode_literals, print_function
import getpass
import os
from argparse import RawDescriptionHelpFormatter
from chalmers import errors
import argparse

if os.name == 'nt':
    from . import _install_service_nt as svs
else:
    from . import _install_service_posix as svs

def main(args):

    if args.action == 'status':
        svs.main_status(args)

    elif args.action == 'install':
        svs.main(args)

    elif args.action == 'uninstall':
        svs.main_uninstall(args)

    else:
        raise errors.ChalmersError("Invalid action %s" % args.action)


def add_parser(subparsers):
    parser = subparsers.add_parser('service',
                                   help='Install chalmers as a service',
                                      description=__doc__,
                                      formatter_class=RawDescriptionHelpFormatter)

    parser.add_argument('action', choices=['install', 'uninstall', 'status'])

    if os.name == 'nt':
        parser.add_argument('-u', '--username', default=getpass.getuser(),
                            help=argparse.SUPPRESS)
        parser.add_argument('--wait', action='store_true', help=argparse.SUPPRESS)


    parser.set_defaults(main=main)

