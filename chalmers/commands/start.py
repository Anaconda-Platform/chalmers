'''
'''
from __future__ import unicode_literals, print_function
import logging
from chalmers.program import Program

log = logging.getLogger('chalmers.start')

def main(args):
    proc = Program(args.name)
    proc.start_async(args.daemon)

def add_parser(subparsers):
    parser = subparsers.add_parser('start',
                                      help='Start a command running',
                                      description=__doc__)

    parser.add_argument('-n', '--name', required=True)
    parser.add_argument('-w', '--wait', '--no-daemon', action='store_false', dest='daemon')
    parser.add_argument('-d', '--daemon', action='store_true', dest='daemon', default=True)

    parser.set_defaults(main=main)
