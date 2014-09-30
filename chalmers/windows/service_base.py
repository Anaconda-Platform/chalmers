from win32serviceutil import ServiceFramework
import os
import sys
import win32event, win32serviceutil, win32service, win32api

import logging
from win32pipe import CreateNamedPipe, ConnectNamedPipe, DisconnectNamedPipe
from win32pipe import PIPE_ACCESS_DUPLEX, PIPE_TYPE_MESSAGE, PIPE_WAIT, PIPE_UNLIMITED_INSTANCES
from win32file import ReadFile, WriteFile
import abc
log = logging.getLogger(__name__)

class WindowsService(object, ServiceFramework):
    __metaclass__ = abc.ABCMeta

    def __init__(self, args):
        sys.stdout = sys.stderr = errlog = open('C:\Users\Administrator\Desktop\service-log.err', 'a')
        print "This is the ChalmersService %r --" % (args,)
        sys.stdout.flush()
        try:
            print "Got Here"; sys.stdout.flush()

            self._svc_name_ = args[0]
            self._svc_display_name_ = args[0]

            ServiceFramework.__init__(self, args)

            name = args[0][9:]

            sys.stdout = sys.stderr = self.errlog = errlog

            log.info('log init')
            self.stop_event = win32event.CreateEvent(None, 0, 0, None)

            print "finished init"; sys.stdout.flush()

        except Exception as err:
            import traceback
            traceback.print_exc(file=errlog)
            raise

    def log(self, msg):
        import servicemanager
        servicemanager.LogInfoMsg(str(msg))
        self.errlog.write('%s:%s\n' % (self._svc_name_, msg))
        self.errlog.flush()


    def sleep(self, sec):
        win32api.Sleep(sec * 1000, True)


    def SvcDoRun(self):
        self.log('start')
        print "starting"

        self.ReportServiceStatus(win32service.SERVICE_START_PENDING)
        try:
            self.ReportServiceStatus(win32service.SERVICE_RUNNING)
            self.log('start')
            self.start()
            self.log('wait')
            win32event.WaitForSingleObject(self.stop_event, win32event.INFINITE)
            self.log('done')
        except Exception, x:
            self.log('Exception : %s' % x)
            self.SvcStop()


    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        self.log('stopping')
        self.stop()
        self.log('stopped')
        win32event.SetEvent(self.stop_event)
        self.ReportServiceStatus(win32service.SERVICE_STOPPED)


service_path = '%s.%s' % (os.path.splitext(__file__)[0], WindowsService.__name__)
