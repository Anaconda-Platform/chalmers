import sys
from chalmers.program import Program
import logging
from clyent.logs import setup_logging
from chalmers.config import dirs
from os.path import join
logger = logging.getLogger('chalmers')
cli_logger = logging.getLogger('cli-logger')

def main():
    logfile = join(dirs.user_log_dir, 'chalmers.log')
    setup_logging(logger, logging.INFO, use_color=False, logfile=logfile, show_tb=True)
    name = sys.argv[1]
    cli_logger.error("Starting program: %s" % name)
    prog = Program(name)
    prog.start_sync()

if __name__ == '__main__':
    main()
