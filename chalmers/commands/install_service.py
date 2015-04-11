'''
[Un]Install chalmers so that it will run at system boot.

For all platforms you can install the service either to the system or locally

When installing For some platforms osx and win32, 
chalmers will only run at login 

Local service install. Admin is not - on some systems (windows) 
this may limit chalmers to starting on login, not boot::

    chalmers service install

This command will install chalmers server to start on 
boot for the current user (posix)::

    sudo chalmers service install
     
This command will install chalmers server to start on 
boot for the root user (posix)::

    sudo chalmers service install --root 

Root service install (windows)::
    
    runas /user:.\Administrator "chalmers service install --system" 
'''
from __future__ import unicode_literals, print_function

from argparse import RawDescriptionHelpFormatter
import argparse
import getpass
import os

from chalmers import errors

from chalmers.service import Service
def main(args):
    service = Service(args.system)

    if args.action == 'status':
        service.status()
    elif args.action == 'install':
        service.install()
    elif args.action == 'uninstall':
        service.uninstall()

    else:
        raise errors.ChalmersError("Invalid action %s" % args.action)


def add_parser(subparsers):
    parser = subparsers.add_parser('service',
                                   help='Install chalmers as a service',
                                      description=__doc__,
                                      formatter_class=RawDescriptionHelpFormatter)

    parser.add_argument('action', choices=['install', 'uninstall', 'status'], nargs='?', default='status')
    group = parser.add_argument_group('Service Type').add_mutually_exclusive_group()

    if os.name == 'posix':
        sytem_default = os.environ.get('SUDO_USER') if os.getuid() == 0 else False
    else:
        sytem_default = False

    group.add_argument('--system', '--system-user', dest='system', default=sytem_default, metavar='USERNAME',
                       help='Install Chalmers as a service to the system for a given user (requires admin). '
                            'If no user is given it will launch chalmers as root (default: %(default)s)')
    group.add_argument('--local', '--no-system', dest='system', action='store_false',
                       help='Always install chalmers service assuming no admin access')
    group.add_argument('--root', '--admin', dest='system', action='store_const', const=None,
                       help='Install Chalmers as a service to the system for the root/admin user '
                       'this argument implies `--system root on unix`')

    if os.name == 'nt':
        parser.add_argument('-u', '--username', default=getpass.getuser(),
                            help=argparse.SUPPRESS)
        parser.add_argument('--wait', action='store_true', help=argparse.SUPPRESS)


    parser.set_defaults(main=main)

