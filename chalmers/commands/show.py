'''
Show the definition file content
'''
from __future__ import unicode_literals, print_function

import logging

from chalmers.program import Program
from chalmers.utils import print_opts
from argparse import RawDescriptionHelpFormatter

log = logging.getLogger('chalmers.show')

def main(args):

    prog = Program(args.name)
    print("Definition file:\n\t%s" % prog.definition_filename)
    print("State file:\n\t%s" % prog.state_filename)
    print('State')
    for key, value in prog.state.items():
        print("%12s: %s" % (key, value))

    if args.raw:
        data = prog.raw_data.copy()
    else:
        data = prog.data.copy()

    for category, opts in Program.OPTIONS:
        print_opts(category, data, opts)

    print_opts('Other Options', data, data.keys())


def add_parser(subparsers):
    parser = subparsers.add_parser('show',
                                      help='Show the definition file content',
                                      description=__doc__,
                                      formatter_class=RawDescriptionHelpFormatter)

    parser.add_argument('name')
    parser.add_argument('-r', '--raw', action='store_true',
                        help='Show the definition file before it is formatted and populated with defaults')
    parser.set_defaults(main=main)
