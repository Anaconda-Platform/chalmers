import logging
from logging.handlers import RotatingFileHandler
from os import makedirs
from os.path import join, exists

from chalmers.config import dirs
from chalmers.utils.handlers import MyStreamHandler

import sys

logger = logging.getLogger('chalmers')

def log_unhandled_exception(*exc_info):
    logger.error('', exc_info=exc_info)
    sys.exit(1)

def setup_logging(level, color=None, logfile='cli.log', short_tb=()):


    if not exists(dirs.user_log_dir): makedirs(dirs.user_log_dir)


    logger.setLevel(logging.DEBUG)

    error_logfile = join(dirs.user_log_dir, logfile)
    hndlr = RotatingFileHandler(error_logfile, maxBytes=10 * (1024 ** 2), backupCount=5,)
    hndlr.setLevel(logging.INFO)
    logger.addHandler(hndlr)

    shndlr = MyStreamHandler(color=color, short_tb=short_tb)
    shndlr.setLevel(level)
    logger.addHandler(shndlr)

    sys.excepthook = log_unhandled_exception

