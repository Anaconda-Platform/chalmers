'''
'''
from __future__ import unicode_literals, print_function

from chalmers.config import dirs
from os import path
from chalmers import errors
import logging
import os
from chalmers.program import Program

log = logging.getLogger('chalmers.remove')

def main(args):

    prog = Program(args.name)
    prog.delete()
    log.info("Program %s removed" % args.name)

def add_parser(subparsers):

    parser = subparsers.add_parser('remove',
                                      help='Remove a command from the chalmers list',
                                      description=__doc__)

    parser.add_argument('-n', '--name', required=True)
    parser.set_defaults(main=main)
