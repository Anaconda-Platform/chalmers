'''
Remove a program definition from chalmers
'''
from __future__ import unicode_literals, print_function

from argparse import RawDescriptionHelpFormatter
import logging
import sys

from chalmers import errors
from chalmers.utils.cli import add_selection_group, select_programs
from clyent.logs.colors.printer import print_colors


log = logging.getLogger('chalmers.remove')

def main(args):

    programs = select_programs(args, filter_paused=False)

    for prog in programs:
        if not prog.exists():
            print("Program '{0}' does not exist".format(prog.name))
            continue

        print("Removing program {0!s:25} ... ".format(prog.name[:25]), end=''); sys.stdout.flush()

        try:
            prog.delete()
        except errors.ChalmersError as err:
            print_colors("[{=ERROR!c:red} ] %s" % err.message, stream=sys.stdout)
            continue

        print_colors("[  {=OK!c:green}  ]", stream=sys.stdout)

def add_parser(subparsers):

    parser = subparsers.add_parser('remove',
                                      help='Remove a program definition from chalmers',
                                      description=__doc__,
                                      formatter_class=RawDescriptionHelpFormatter)

    add_selection_group(parser)

    parser.set_defaults(main=main)
