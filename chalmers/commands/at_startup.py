'''
Enable/Disable chalmers so that it will run at machine startup.

This command requires root/admin access for all platforms.

If you need to enable chalmers as a service without admin try::

    chalmers @login --help

This command will install chalmers server to start on
boot for the current user (posix)::

    sudo chalmers @starup enable

This command will install chalmers server to start on
boot for a target user (posix)::

    sudo chalmers service install --root

Root service install (windows)::
    
    runas /user:.\Administrator "chalmers @startup enable"
'''

from __future__ import unicode_literals, print_function

from argparse import RawDescriptionHelpFormatter
import os

from chalmers import errors
from chalmers.service import SystemService


def main(args):


    if os.name == 'nt':
        from win32com.shell import shell
        if not shell.IsUserAnAdmin():
            raise errors.ChalmersError('You must be an administrator to run this command')
    else:
        if os.getuid() != 0:
            raise errors.ChalmersError('You must be root to run this command')

    service = SystemService(args.target_user)

    if args.action == 'status':
        service.status()
    elif args.action == 'enable':
        service.install()
    elif args.action == 'disable':
        service.uninstall()

    else:
        raise errors.ChalmersError("Invalid action %s" % args.action)


def add_parser(subparsers):
    parser = subparsers.add_parser('@startup',
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

