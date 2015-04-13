import logging
import os
import signal
import subprocess
import sys

from pywintypes import error as Win32Error
from win32api import OpenProcess
from win32event import SYNCHRONIZE
from win32file import CloseHandle

from .base import ProgramBase
from chalmers import errors


log = logging.getLogger(__name__)

class NTProgram(ProgramBase):
    """
    Program that implements ProgramBase's abstract
    methods for the win32 platform
    """

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

        cmd = [sys.executable, script]

        if 'CHALMERS_ROOT' in os.environ:
            cmd.extend(['--root', os.environ['CHALMERS_ROOT']])

        cmd.append(self.name)
        creationflags = subprocess.CREATE_NEW_CONSOLE | subprocess.CREATE_NEW_PROCESS_GROUP
        p0 = subprocess.Popen(cmd,
                              creationflags=creationflags,
                              startupinfo=startupinfo,
                              close_fds=True)


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
        log.error("Send Signal pid=%s sig=%s SIGINT=%s" % (pid, sig, signal.SIGINT))
        if sig == signal.SIGINT:
            os.kill(signal.CTRL_C_EVENT, 0)
            return

        if sig != signal.SIGTERM:
            log.error("Can not kill process with signal %s on windows. Using SIGTERM (%i)" % (sig, signal.SIGTERM))

        PROCESS_TERMINATE = 1
        ExitCode = -1
        handle = ctypes.windll.kernel32.OpenProcess(PROCESS_TERMINATE, False, pid)
        ctypes.windll.kernel32.TerminateProcess(handle, ExitCode)
        ctypes.windll.kernel32.CloseHandle(handle)
