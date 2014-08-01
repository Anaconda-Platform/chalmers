"""
Chalmers runner helper
"""
from __future__ import unicode_literals, print_function
from chalmers import __version__ as version, make_program_data
import sys
from argparse import ArgumentParser
import yaml
import os
import time
from subprocess import Popen, STDOUT
import logging
from chalmers.utils.logutil import setup_logging
import signal
from chalmers.process import Process
from chalmers.utils.daemonize import daemonize

log = logging.getLogger('chalmers.runner')

class StopProcess(Exception):
    pass

def stop_process(signum, frame):
    raise StopProcess()

def keep_alive(data):

    signal.signal(signal.SIGUSR2, stop_process)
    signal.signal(signal.SIGALRM, stop_process)

    if data['redirect_stderr']:
        stderr = STDOUT
    else:
        stderr = open(data['stderr'], 'a')

    stdout = open(data['stdout'], 'a')

    log.info('Running command: %s' % ' '.join(data['command']))

    p0 = None
    status = 0
    try:
        for i in range(data['retries'] + 1):
            start = time.time()
            if i:
                log.info('Retry command (%i of %i)' % (i, data['retries']))
            p0 = Popen(data['command'], stdout=stdout, stderr=stderr)
            log.info('Program started with pid %s' % p0.pid)

            status = p0.wait()
            p0 = None

            uptime = time.time() - start

            log.info('Command Exited with status %s' % status)
            log.info(' + Uptime %s' % uptime)
            if uptime < data['startsecs']:
                return "Error: Program could not successfully start"

            if status in data['exitcodes']:
                return "Stopped: Program exited gracefully"

    except StopProcess:
        log.info('Stop Process Requested')
        if p0:
            log.info('Sending signal %s to process %s' % (data['stopsignal'], p0.pid))
            p0.send_signal(data['stopsignal'])
            if data['stopwaitsecs']:
                signal.alarm(data['stopwaitsecs'])

            try:
                status = p0.wait()
                log.info('Command Exited with status %s' % status)
                return "Stopped: At user request"
            except StopProcess:
                log.info('Process %s did not exit within %s seconds sending SIGKILL' % (p0.pid, data['stopwaitsecs']))
                p0.send_signal(signal.SIGKILL)

    return 'Error: Program exited with status %s' % status



def main(argv=None):
    if argv is None: argv = sys.argv

    parser = ArgumentParser(description=__doc__)
    parser.add_argument('-v', '--verbose',
                        action='store_const', help='print debug information ot the console',
                        dest='log_level',
                        default=logging.INFO, const=logging.DEBUG)
    parser.add_argument('-q', '--quiet',
                        action='store_const', help='Only show warnings or errors the console',
                        dest='log_level', const=logging.WARNING)
    parser.add_argument('-V', '--version', action='version',
                        version="%%(prog)s Command line client (version %s)" % (version,))

    parser.add_argument('definition')
    parser.add_argument('-n', '--nodaemon', action='store_false', dest='daemon')
    parser.add_argument('-d', '--daemon', action='store_true', dest='daemon', default=True)
    args = parser.parse_args(argv[1:])

    setup_logging(args)

    proc = Process(args.definition)

    log.info('Startg chalmers runner pid=%s' % os.getpid())

    proc.start_async(args.daemon)

if __name__ == '__main__':
    main(sys.argv)
