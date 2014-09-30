'''
'''
from __future__ import unicode_literals, print_function

import logging

from chalmers.program_manager import ProgramManager
from chalmers.event_dispatcher import send_action

log = logging.getLogger('chalmers.manager')

def main(args):

    if args.is_running:
        try:
            result = send_action("chalmers", "ping")
        except:
            log.info("Manager is NOT running")
        else:
            log.info("Manager is running with pid %s" % result)
        return 
    if args.shutdown:
        send_action("chalmers", "exitloop")
        log.info("Manager is shutting down")
        return
    log.info("Managing processes")
    mgr = ProgramManager(use_color=args.color)
    mgr.start_all()
    mgr.listen()


def add_parser(subparsers):
    parser = subparsers.add_parser('manager',
                                   help='Manage Chalmers programs',
                                      description=__doc__)

    parser.add_argument("--shutdown", action='store_true',
                help="Exit manager")
    parser.add_argument("--is-running", action='store_true',
                help="Check if the manager is running")
    parser.set_defaults(main=main)
