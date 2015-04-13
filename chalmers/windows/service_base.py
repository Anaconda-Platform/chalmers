import abc
import logging
import traceback

import servicemanager
import win32event, win32service, win32api
from win32serviceutil import ServiceFramework


log = logging.getLogger(__name__)

class WindowsService(object, ServiceFramework):
    """
    Base windows service class that provides all the nice things that a python
    service needs
    """
    __metaclass__ = abc.ABCMeta

    def __init__(self, args):
        try:

            self._svc_name_ = args[0]
            self._svc_display_name_ = args[0]

            ServiceFramework.__init__(self, args)
            self.stop_event = win32event.CreateEvent(None, 0, 0, None)

        except Exception:
            self.log("Error in WindowsService.__init__")
            self.log(traceback.format_exc())
            raise

    def log(self, msg):
        'Log to the NTEventlog'
        servicemanager.LogInfoMsg(str(msg))

    def sleep(self, sec):
        win32api.Sleep(sec * 1000, True)


    def SvcDoRun(self):
        self.log('start')

        self.ReportServiceStatus(win32service.SERVICE_START_PENDING)
        try:
            self.ReportServiceStatus(win32service.SERVICE_RUNNING)
            self.log('start')
            self.start()

            self.ReportServiceStatus(win32service.SERVICE_STOPPED)
#             self.log('wait')
#             win32event.WaitForSingleObject(self.stop_event, win32event.INFINITE)
            self.log('done')
        except Exception:
            self.log("Error in WindowsService.SvcDoRun")
            self.log(traceback.format_exc())
            self.SvcStop()


    def SvcStop(self):
        pass
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        self.log('stopping')
        self.stop()
        self.log('stopped')
        win32event.SetEvent(self.stop_event)
        self.ReportServiceStatus(win32service.SERVICE_STOPPED)


