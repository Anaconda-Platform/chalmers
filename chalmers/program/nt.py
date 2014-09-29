from .base import ProgramBase
from win32serviceutil import QueryServiceStatus, InstallService, StartService, StopService, RemoveService, DebugService
from win32service import SERVICE_AUTO_START, SERVICE_RUNNING
from pywintypes import error as Win32Error
from windows_service import service_path, ChalmersService
from win32api import SetConsoleCtrlHandler
import logging


log = logging.getLogger(__name__)

class Program(ProgramBase):
    
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
      
        service_name = 'chalmers:{self.name}'.format(self=self)
        if not self.is_installed:
            SetConsoleCtrlHandler(lambda x: True, True)
            log.info('Windows install service %s' % service_path)
            InstallService(
                service_path,
                self.svs_name, self.svs_name,
                startType = SERVICE_AUTO_START
            )
        log.info('Windows start service %s' % self.svs_name)
        StartService(self.svs_name)


    def stop(self):

        if self.is_running:
            StopService(self.svs_name)
            log.info('Windows stopping service %s' % self.svs_name)

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
