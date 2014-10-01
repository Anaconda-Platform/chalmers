'''
Chalmers command line utility
'''
from __future__ import print_function, unicode_literals

from argparse import ArgumentParser
import logging

from chalmers import __version__ as version
from chalmers.commands import sub_commands
from chalmers.errors import ChalmersError, ShowHelp
from chalmers.utils.logutil import setup_logging


logger = logging.getLogger('chalmers')


def main(args=None, exit=True):


    parser = ArgumentParser(description=__doc__)
    parser.add_argument('--show-traceback', action='store_true')
    parser.add_argument('-v', '--verbose',
                        action='store_const', help='print debug information ot the console',
                        dest='log_level',
                        default=logging.INFO, const=logging.DEBUG)
    parser.add_argument('-q', '--quiet',
                        action='store_const', help='Only show warnings or errors the console',
                        dest='log_level', const=logging.WARNING)
    parser.add_argument('-V', '--version', action='version',
                        version="%%(prog)s Command line client (version %s)" % (version,))
    parser.add_argument('--color', action='store_true', default=None,
                        help='always display with colors')
    parser.add_argument('--no-color', action='store_false', dest='color',
                        help='never display with colors')
    subparsers = parser.add_subparsers(help='commands')

    for command in sub_commands():
        command.add_parser(subparsers)

    args = parser.parse_args(args)

    short_tb = ()

    if not args.show_traceback:
        short_tb = (ChalmersError, KeyboardInterrupt)

    setup_logging(args.log_level, args.color, short_tb=short_tb)

    try:
        return args.main(args)

    except ShowHelp as err:
        args.sub_parser.print_help()
        if exit:
            raise SystemExit(1)
        else:
            return 1

if __name__ == "__main__":
    main()
