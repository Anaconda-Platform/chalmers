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


    def handle_signals(self):
        self._ignore_sigint = 0
        #signal.signal(signal.SIGINT, self.sigint_handler)




    def start_as_service(self):
        """
        Run this program in a new background process

        posix only
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


    def dispatch_bg(self):
        raise errors.ChalmersError("Can not yet move a win32 process to the background")

    def _send_signal(self, pid, sig):
        # Kill the proces using ctypes and pid
        
        import ctypes

        if sig == signal.SIGINT:
             self._ignore_sigint = 0 
             SetConsoleCtrlHandler(sigint_handler, True)
             res = ctypes.windll.kernel32.GenerateConsoleCtrlEvent(0, pid)
             return

        if sig != signal.SIGTERM:
            log.error("Can not kill process with signal %s on windows. Using SIGTERM (%i)" % (sig, signal.SIGTERM) )
        
        PROCESS_TERMINATE = 1
        handle = ctypes.windll.kernel32.OpenProcess(PROCESS_TERMINATE, False, pid)
        ctypes.windll.kernel32.TerminateProcess(handle, -1)
        ctypes.windll.kernel32.CloseHandle(handle)