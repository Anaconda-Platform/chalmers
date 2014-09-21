'''
'''
from __future__ import unicode_literals, print_function

import logging

from chalmers.program import Program

log = logging.getLogger('chalmers.remove')

def main(args):

    prog = Program(args.name)
    prog.delete()
    log.info("Program %s removed" % args.name)

def add_parser(subparsers):

    parser = subparsers.add_parser('remove',
                                      help='Remove a command from the config',
                                      description=__doc__)

    parser.add_argument('name')
    parser.set_defaults(main=main)
