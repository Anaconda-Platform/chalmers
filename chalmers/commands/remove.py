'''
'''
from __future__ import unicode_literals, print_function

from argparse import RawDescriptionHelpFormatter
import logging
import sys

from chalmers import errors
from chalmers.program import Program
from clyent.logs.colors.printer import print_colors


log = logging.getLogger('chalmers.remove')

def main(args):

    programs = [Program(name) for name in args.names]
    for prog in programs:
        if not prog.exists():
            print("Program '{0}' does not exist".format(prog.name))
            continue

        print("Removing program {0!s:25} ... ".format(name[:25]), end=''); sys.stdout.flush()

        try:
            prog.delete()
        except errors.ChalmersError as err:
            print_colors("[{=ERROR!c:red} ] {0}".format(err.message), stream=sys.stdout)
            continue


        print_colors("[  {=OK!c:green}  ]", stream=sys.stdout)

def add_parser(subparsers):

    parser = subparsers.add_parser('remove',
                                      help='Remove a program definition from chalmers',
                                      description=__doc__,
                                      formatter_class=RawDescriptionHelpFormatter)

    parser.add_argument('names', nargs='*', metavar='PROG')
    parser.set_defaults(main=main)
