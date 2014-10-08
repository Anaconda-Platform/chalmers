'''
'''
from __future__ import unicode_literals, print_function

from argparse import RawDescriptionHelpFormatter
import logging

from chalmers.program import Program
import sys
from chalmers import errors


log = logging.getLogger('chalmers.remove')

def main(args):

    programs = [Program(name) for name in args.names]
    for prog in programs:

        print("Removing program {0!s:25} ... ".format(name[:25]), end=''); sys.stdout.flush()

        try:
            prog.delete()
        except errors.ChalmersError as err:
            print("[ERROR ] {0}".format(err.message))
            continue


        print("[  OK  ]")

def add_parser(subparsers):

    parser = subparsers.add_parser('remove',
                                      help='Remove a program definition from chalmers',
                                      description=__doc__,
                                      formatter_class=RawDescriptionHelpFormatter)

    parser.add_argument('names', nargs='*', metavar='PROG')
    parser.set_defaults(main=main)
