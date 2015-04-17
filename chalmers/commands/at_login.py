'''
Enable/Disable chalmers so that it will run at user login.

This command does not require root/admin access for all platforms.

This command will install chalmers server to start at
login for the current user (posix)::

    chalmers @login enable

If you want to enable chalmers as a system wide service try::
    
    chalmers @startup --help
'''

from __future__ import unicode_literals, print_function

from argparse import RawDescriptionHelpFormatter
import logging
import os

from chalmers import errors
from chalmers.service import LocalService


log = logging.getLogger(__name__)

def main(args):

    service = LocalService(False)

    if args.action == 'status':
        service.status()
    elif args.action == 'enable':
        service.install()
    elif args.action == 'disable':
        service.uninstall()

    else:
        raise errors.ChalmersError("Invalid action %s" % args.action)


def add_parser(subparsers):
    parser = subparsers.add_parser('@login',
                                   help='Install chalmers as a service',
                                      description=__doc__,
                                      formatter_class=RawDescriptionHelpFormatter)

    parser.add_argument('action', choices=['enable', 'disable', 'status'], nargs='?', default='status')
    group = parser.add_argument_group('Service Type').add_mutually_exclusive_group()

    if os.name == 'posix':
        sytem_default = os.environ.get('SUDO_USER') if os.getuid() == 0 else None
    else:
        sytem_default = None

    group.add_argument('--user', dest='target_user', default=sytem_default, metavar='USERNAME',
                       help='Install Chalmers as a service to the system for a given user (requires admin). '
                            'If no user is given it will launch chalmers as root (default: %(default)s)')

    parser.set_defaults(main=main)

