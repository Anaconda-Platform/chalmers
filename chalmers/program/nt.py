import logging
import os
import subprocess
import sys
import signal

from pywintypes import error as Win32Error
from win32api import OpenProcess, SetConsoleCtrlHandler
from win32event import SYNCHRONIZE
from win32file import CloseHandle

from chalmers import errors

from .base import ProgramBase

def sigint_handler(signum, frame=None):
    log.warn("Program received signal %s ignoring" % (signum))
    SetConsoleCtrlHandler(sigint_handler, False)

log = logging.getLogger(__name__)

class NTProgram(ProgramBase):


    @property
    def is_running(self):

        pid = self.state.get('pid')
        if not pid:
            return False

        try:
            handle = OpenProcess(SYNCHRONIZE, 0, pid)
            CloseHandle(handle)
            return True
        except Win32Error:
            return False


    def start_as_service(self):
        """
        Run this program in a new background process

        windows only
        """

        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = subprocess.SW_HIDE

        from chalmers.scripts import runner as runner_script

        script = os.path.abspath(runner_script.__file__)

        if script.endswith('.pyc') or script.endswith('.pyo'):
            script = script[:-1]

        cmd = [sys.executable, script, self.name]
        p0 = subprocess.Popen(cmd,
                              creationflags=subprocess.CREATE_NEW_CONSOLE,
                              startupinfo=startupinfo)


    def handle_signals(self):
        # Called before keep_alive

        new_mask = self.data.get('umask')
        if new_mask:
            log.warning("Config var 'umask' will be ignored on win32")

        user = self.data.get('user')

        if user:
            raise errors.ChalmersError("Can not yet run as program as a user on win32")


    def dispatch_bg(self):
        raise errors.ChalmersError("Can not yet move a win32 process to the background")

    def _send_signal(self, pid, sig):
        'Kill the process using ctypes and pid'

        import ctypes

        if sig == signal.SIGINT:
            self._ignore_sigint = 0
            # Set the handler so the main thread of this process does not catch it
            # sigint_handler removes itself once caught
            SetConsoleCtrlHandler(sigint_handler, True)
            res = ctypes.windll.kernel32.GenerateConsoleCtrlEvent(0, pid)
            return

        if sig != signal.SIGTERM:
            log.error("Can not kill process with signal %s on windows. Using SIGTERM (%i)" % (sig, signal.SIGTERM))

        PROCESS_TERMINATE = 1
        ExitCode = -1
        handle = ctypes.windll.kernel32.OpenProcess(PROCESS_TERMINATE, False, pid)
        ctypes.windll.kernel32.TerminateProcess(handle, ExitCode)
        ctypes.windll.kernel32.CloseHandle(handle)
