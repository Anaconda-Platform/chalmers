import logging

from pywintypes import error as Win32Error
from win32api import OpenProcess
from win32file import CloseHandle
from win32event import SYNCHRONIZE

from .base import ProgramBase
import subprocess
import sys
import os


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




