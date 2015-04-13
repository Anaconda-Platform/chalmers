'''
Chalmers main script

This script loads all of the chalmers commands
'''
from __future__ import print_function, unicode_literals

from argparse import ArgumentParser
import logging

from clyent import add_default_arguments, add_subparser_modules, run_command
from clyent.logs import setup_logging

from chalmers import __version__ as version
from chalmers import config
import chalmers.commands


logger = logging.getLogger('chalmers')

def main(args=None, exit=True):

    parser = ArgumentParser(description=__doc__)

    add_default_arguments(parser, version)
    add_subparser_modules(parser, chalmers.commands)

    args = parser.parse_args(args)
    logfile = config.main_logfile()
    setup_logging(logger, args.log_level, use_color=args.color,
                  show_tb=args.show_traceback, logfile=logfile)

    if not hasattr(args, 'main'):
        parser.error('too few arguments')

    run_command(args, exit=exit)

if __name__ == "__main__":
    main()
