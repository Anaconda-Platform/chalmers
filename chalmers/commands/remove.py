'''
'''
from __future__ import unicode_literals, print_function

from argparse import RawDescriptionHelpFormatter
import logging

from chalmers.program import Program


log = logging.getLogger('chalmers.remove')

def main(args):

    prog = Program(args.name)
    prog.delete()
    log.info("Program %s removed" % args.name)

def add_parser(subparsers):

    parser = subparsers.add_parser('remove',
                                      help='Remove a program definition from chalmers',
                                      description=__doc__,
                                      formatter_class=RawDescriptionHelpFormatter)

    parser.add_argument('name')
    parser.set_defaults(main=main)
