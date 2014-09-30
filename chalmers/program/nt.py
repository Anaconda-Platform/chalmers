import logging

from pywintypes import error as Win32Error
from win32api import OpenProcess
from win32file import CloseHandle
from win32event import SYNCHRONIZE

from .base import ProgramBase


log = logging.getLogger(__name__)

class NTProgram(ProgramBase):


    @property
    def is_running(self):

        pid = self.state.get('pid')
        if not pid:
            return False

        try:
            handle = OpenProcess(SYNCHRONIZE, 0, pid)
            return True
        except Win32Error:
            return False
        finally:
            CloseHandle(handle)

