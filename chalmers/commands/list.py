'''
'''
from __future__ import unicode_literals, print_function

import logging

from chalmers.program import Program


log = logging.getLogger(__name__)

def main(args):

    programs = list(Program.find_for_user())

    for prog in programs:
        log.info('[%s], %s' % (prog.data['name'], prog.text_status))

    if not programs:
        print('No programs added')


def add_parser(subparsers):
    parser = subparsers.add_parser('list',
                                      help='List registered commands',
                                      description=__doc__)

    parser.set_defaults(main=main)
