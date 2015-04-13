"""
Chalmers program runner (for windows)

Instead of daemonizing the process like posix,
win32 runs this run script with Popen

Chalmers runs this programm hidden by default
"""

from argparse import ArgumentParser
import logging

from clyent.logs import setup_logging

from chalmers import config
from chalmers.program import Program


logger = logging.getLogger('chalmers')
cli_logger = logging.getLogger('cli-logger')

def main():

    parser = ArgumentParser(description=__doc__)
    parser.add_argument('--root', help='chalmers root config directory')
    parser.add_argument('name', help='name of program to run')
    args = parser.parse_args()

    if args.root:
        config.set_relative_dirs(args.root)


    logfile = config.main_logfile()
    setup_logging(logger, logging.INFO, use_color=False, logfile=logfile, show_tb=True)
    cli_logger.error("Starting program: %s" % args.name)
    prog = Program(args.name)
    prog.start_sync()

if __name__ == '__main__':
    main()
