import logging
import os
import signal
import sys

from chalmers import errors
from chalmers.utils.daemonize import daemonize

from .base import ProgramBase


log = logging.getLogger(__name__)


def stop_process(signum, frame):
    """
    Signal handler to raise StopProcess exception
    """
    log.debug("Process recieved signal %s" % signum)
    raise errors.StopProcess()

class PosixProgram(ProgramBase):

    @property
    def is_running(self):
        "Check For the existence of a pid"
        pid = self.state.get('pid')
        if not pid:
            return False
        try:
            os.kill(pid, 0)
        except OSError:
            return False
        else:
            return True

    def start_as_service(self):
        """
        Run this program in a new background process

        posix only
        """

        daemonize(self.start_sync)

    def sighup_handler(self, signum, frame):
        if self._ignore_sighup:
            log.warn("Program %s received signal %s ignoring" % (self.name, signum))
        else:
            log.error("Program %s received signal %s exiting" % (self.name, signum))
            sys.exit(-1)

    def handle_signals(self):
        self._ignore_sighup = False
        signal.signal(signal.SIGHUP, self.sighup_handler)

    def clear_socket(self):
        'Remove socket file'
        if os.path.exists(self.addr):
            log.debug("Removing socket file %s" % self.addr)
            try:
                os.unlink(self.addr)
            except OSError as err:
                log.warn("Error: %s" % err)


    def stop(self):
        try:
            ProgramBase.stop(self)
        finally:
            self.clear_socket()


    def dispatch_bg(self):
        log.warn("Moving process to the background")

        if self.pipe_output:
            print("Output is written to '%s'" % self.data['stdout'])
            self._echo.stop()

        log.warn("Ignoring sighup (%i)" % signal.SIGHUP)

        self._ignore_sighup = True

        si = file('/dev/null', 'r')
        so = file('/dev/null', 'a+')
        se = file('/dev/null', 'a+', 0)
        os.dup2(si.fileno(), sys.stdin.fileno())
        os.dup2(so.fileno(), sys.stdout.fileno())
        os.dup2(se.fileno(), sys.stderr.fileno())


    def preexec_fn(self):
        signal.signal(signal.SIGHUP, signal.SIG_IGN)


