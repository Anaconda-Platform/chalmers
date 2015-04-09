'''
[Un]Install chalmers so that it will run at system boot

This set is required on win32 platforms:

eg:
   
    chalmers service install
    
'''
from __future__ import unicode_literals, print_function

from argparse import RawDescriptionHelpFormatter
import argparse
import getpass
import os

from chalmers import errors

from chalmers import service
def main(args):

    if args.action == 'status':
        service.status(args)

    elif args.action == 'install':
        service.install(args)

    elif args.action == 'uninstall':
        service.uninstall(args)

    else:
        raise errors.ChalmersError("Invalid action %s" % args.action)


def add_parser(subparsers):
    parser = subparsers.add_parser('service',
                                   help='Install chalmers as a service',
                                      description=__doc__,
                                      formatter_class=RawDescriptionHelpFormatter)

    parser.add_argument('action', choices=['install', 'uninstall', 'status'])
    group = parser.add_argument_group('Service Type').add_mutually_exclusive_group()

    if os.name == 'posix':
        sytem_default = os.environ.get('SUDO_USER') if os.getuid() == 0 else False
    else:
        sytem_default = False

    group.add_argument('--system', dest='system', nargs='?', default=sytem_default,
                       help='Install Chalmers as a service to the system for a given user (requires admin). '
                            'If no user is given it will launch chalmers as root (default: %(default)s)')
    group.add_argument('--no-system', dest='system', action='store_false',
                       help='Always install chalmers service assuming no admin access')
    group.add_argument('--root', '--admin', dest='system', action='store_const', const=None,
                       help='Install Chalmers as a service to the system for the root/admin user')

    if os.name == 'nt':
        parser.add_argument('-u', '--username', default=getpass.getuser(),
                            help=argparse.SUPPRESS)
        parser.add_argument('--wait', action='store_true', help=argparse.SUPPRESS)


    parser.set_defaults(main=main)

