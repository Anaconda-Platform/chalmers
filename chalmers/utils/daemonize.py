'''
Uitility for deamonizing linux processes
'''
import logging
import os
import sys


log = logging.getLogger(__name__)

def daemonize(target, stream=None):
    """
    do the UNIX double-fork magic, see Stevens' "Advanced 
    Programming in the UNIX Environment" for details (ISBN 0201563177)
    http://www.erlenstar.demon.co.uk/unix/faq_2.html#SEC16
    """
    pid = os.fork()
    if pid > 0:
        # exit first parent
        return

    # decouple from parent environment
    os.chdir("/")
#     os.setsid()
#     os.umask(0)

    # do second fork
    pid = os.fork()
    if pid > 0:
        # exit from second parent
        sys.exit(0)

    # redirect standard file descriptors
    sys.stdout.flush()
    sys.stderr.flush()

    si = open('/dev/null', 'r')
    so = open('/dev/null', 'a+')
    se = open('/dev/null', 'a+')

    os.dup2(si.fileno(), sys.stdin.fileno())
    os.dup2(so.fileno(), sys.stdout.fileno())
    os.dup2(se.fileno(), sys.stderr.fileno())

    if stream:
        sys.stdin = stream
        sys.stderr = stream

    # Run function as daemon
    target()
    sys.exit(0)
