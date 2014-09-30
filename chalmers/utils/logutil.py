import logging
from logging.handlers import RotatingFileHandler
from os import makedirs
from os.path import join, exists

from chalmers.config import dirs
from chalmers.utils.handlers import MyStreamHandler

import sys
import traceback

logger = logging.getLogger('chalmers')

def log_unhandled_exception(*exc_info):
    logger.error('', exc_info=exc_info)
    logger.error('\n' + ''.join(traceback.format_exception(*exc_info)))
    sys.exit(1)

def setup_logging(args):


    if not exists(dirs.user_log_dir): makedirs(dirs.user_log_dir)


    logger.setLevel(logging.DEBUG)

    error_logfile = join(dirs.user_log_dir, 'cli.log')
    hndlr = RotatingFileHandler(error_logfile, maxBytes=10 * (1024 ** 2), backupCount=5,)
    hndlr.setLevel(logging.INFO)
    logger.addHandler(hndlr)

    shndlr = MyStreamHandler(color=args.color)
    shndlr.setLevel(args.log_level)
    logger.addHandler(shndlr)

    sys.excepthook = log_unhandled_exception

