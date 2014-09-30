'''
'''
from __future__ import unicode_literals, print_function

import logging

from chalmers.program_manager import ProgramManager

log = logging.getLogger('chalmers.manager')

def main(args):

    log.info("Managing processes")

    mgr = ProgramManager()
    mgr.start_all()
    mgr.listen()

    mgr.cleanup()


def add_parser(subparsers):
    parser = subparsers.add_parser('manager',
                                      help='Manage Chalmers programs',
                                      description=__doc__)

    parser.set_defaults(main=main)
