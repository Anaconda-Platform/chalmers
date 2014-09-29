from .base import ProgramBase

class Program(ProgramBase):

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

        if 'daemon_log' in self.data:
           self.log_to_daemonlog()
            log_stream = open(self.data['daemon_log'], 'a')
            hdlr = logging.StreamHandler(log_stream)
#             hdlr = logging.FileHandler(self.data['daemon_log'])
            fmt = logging.Formatter(logging.BASIC_FORMAT)
            hdlr.setFormatter(fmt)
            logging.getLogger('chalmers').addHandler(hdlr)

        daemonize(self.start_sync, stream=self._log_stream)


    def stop(self):
        """
        Stop this program
        
        Sends SIGUSR2 signal to the program's PID
        """

        if not self.is_running:
            raise errors.StateError("Program is not running")
        pid = self.state.get('pid')
        os.kill(pid, signal.SIGUSR2)

        # TODO: not sure how to wait for the PID
        while self.is_running:
            time.sleep(.1)

        self.update_state(pid=None, paused=True)
