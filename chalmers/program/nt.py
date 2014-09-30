import logging
import signal
from threading import Thread

from pywintypes import error as Win32Error
from win32api import SetConsoleCtrlHandler
from win32file import ReadFile, WriteFile
import win32file
from win32pipe import CreateNamedPipe, DisconnectNamedPipe, ConnectNamedPipe
from win32pipe import PIPE_ACCESS_DUPLEX, PIPE_TYPE_MESSAGE, PIPE_WAIT, PIPE_UNLIMITED_INSTANCES
from win32pipe import SetNamedPipeHandleState, PIPE_READMODE_MESSAGE
from win32service import SERVICE_AUTO_START, SERVICE_RUNNING
from win32serviceutil import QueryServiceStatus, InstallService, StartService, StopService, \
    RemoveService, DebugService

from .base import ProgramBase


log = logging.getLogger(__name__)

class NTProgram(ProgramBase):

    @property
    def svs_name(self):
        return 'chalmers:{self.name}'.format(self=self)


    @property
    def is_running(self):

        try:
            status = QueryServiceStatus(self.svs_name)
        except Win32Error as err:
            print "service", self.svs_name, "is not installed"
            return False
        return status[1] == SERVICE_RUNNING

    @property
    def is_installed(self):

        try:
            status = QueryServiceStatus(self.svs_name)
            return True
        except Win32Error as err:
            return False



    def start_as_service(self):

        # Chalmers main process ctrl
        full_name = r'\\.\pipe\chalmers'

        fileHanle = win32file.CreateFile(full_name,
                          win32file.GENERIC_READ | win32file.GENERIC_WRITE,
                          0, None,
                          win32file.OPEN_EXISTING,
                          0, None)
        win32file.WriteFile(fileHanle, "start %s" % self.name)
        win32file.CloseHandle(fileHanle)

    def stop(self):

        if self.is_running:
            full_name = r'\\.\pipe\%s' % self.svs_name
            fileHanle = win32file.CreateFile(full_name,
                              win32file.GENERIC_READ | win32file.GENERIC_WRITE,
                              0, None,
                              win32file.OPEN_EXISTING,
                              0, None)

            win32file.WriteFile(fileHanle, "stop")
            win32file.CloseHandle(fileHanle)

    def delete(self):

        if not self.is_installed:
            log.info('Windows service %s is not installed' % self.svs_name)
            return
        try:
            RemoveService(self.svs_name)
        except Win32Error as err:
            log.error('Windows could not remove service %s' % self.svs_name)
            log.error(str(err))

        ProgramBase.delete(self)

    def setup_termination(self):
        self._ctrl_thead = Thread(target=self.named_pipe_events,)
#         self._ctrl_thead.daemon(True)
        self._ctrl_thead.start()

    BUFFER_SIZE = 512

    def named_pipe_reader(self):
        full_name = r'\\.\pipe\%s' % self.svs_name

        pipeHandle = CreateNamedPipe(full_name,
            PIPE_ACCESS_DUPLEX,
            PIPE_TYPE_MESSAGE | PIPE_WAIT,
            PIPE_UNLIMITED_INSTANCES, self.BUFFER_SIZE, self.BUFFER_SIZE,
            300, None)

        while 1:
            ConnectNamedPipe(pipeHandle, None)

            _, msg = ReadFile(pipeHandle, self.BUFFER_SIZE)

            if msg == 'stop':
                self._p0.send_signal(signal.SIGTERM)
                WriteFile(pipeHandle, "ok")
                break
            else:
                WriteFile(pipeHandle, "ok")
                log.error("Got unknown message from named pipe %r" % msg)

            DisconnectNamedPipe(pipeHandle)

