import logging
import os

from chalmers import errors
from chalmers.event_handler import send_action

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

        send_action('chalmers', 'start', self.name)
#         daemonize(self.start_sync, stream=self._log_stream)


    def clear_socket(self):
        if os.path.exists(self.addr):
            log.debug("Removing socket file %s" % self.addr)
            os.unlink(self.addr)


    def stop(self):
        try:
            ProgramBase.stop(self)
        finally:
            self.clear_socket()

