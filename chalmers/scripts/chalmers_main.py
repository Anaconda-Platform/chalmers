'''
Chalmers command line utility
'''
from __future__ import print_function, unicode_literals
from argparse import ArgumentParser
from chalmers import __version__ as version
from chalmers.commands import sub_commands
from chalmers.errors import ChalmersError, ShowHelp
import logging
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
    subparsers = parser.add_subparsers(help='commands')

    for command in sub_commands():
        command.add_parser(subparsers)

    args = parser.parse_args(args)

    setup_logging(args)
    try:
        return args.main(args)

    except ShowHelp as err:
        args.sub_parser.print_help()
        if exit:
            raise SystemExit(1)
        else:
            return 1

    except (ChalmersError, KeyboardInterrupt) as err:
        if args.show_traceback:
            raise
        if hasattr(err, 'message'):
            logger.exception(err.message)
        elif hasattr(err, 'args'):
            logger.exception(err.args[0] if err.args else '')
        else:
            logger.exception(str(err))
        if exit:
            raise SystemExit(1)
        else:
            return 1

