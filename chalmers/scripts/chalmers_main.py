'''
Chalmers command line utility
'''
from __future__ import print_function, unicode_literals

from argparse import ArgumentParser
import logging

from chalmers import __version__ as version
import chalmers.commands
from clyent import add_default_arguments, add_subparser_modules, run_command
from clyent.logs import setup_logging
from chalmers.config import dirs
from os.path import join


logger = logging.getLogger('chalmers')

def main(args=None, exit=True):

    parser = ArgumentParser(description=__doc__)

    add_default_arguments(parser, version)
    add_subparser_modules(parser, chalmers.commands)

    args = parser.parse_args(args)
    logfile = join(dirs.user_log_dir, 'chalmers.log')
    setup_logging(logger, args.log_level, use_color=args.color,
                  show_tb=args.show_traceback, logfile=logfile)

    run_command(args, exit=exit)

if __name__ == "__main__":
    main()
