from win32serviceutil import ServiceFramework
import os
import sys
import win32event, win32serviceutil, win32service, win32api

import logging
from chalmers.program.nt import Program
from win32pipe import CreateNamedPipe, ConnectNamedPipe, DisconnectNamedPipe
from win32pipe import PIPE_ACCESS_DUPLEX, PIPE_TYPE_MESSAGE, PIPE_WAIT, PIPE_UNLIMITED_INSTANCES
from win32file import ReadFile, WriteFile

log = logging.getLogger(__name__)

class ChalmersService(ServiceFramework):

    def __init__(self, args):
        sys.stdout = sys.stderr = errlog = open('C:\Users\Administrator\Desktop\clog.err', 'a')
        print "This is the ChalmersService %r --" % (args,)
        sys.stdout.flush()
        try:
            print "Got Here"; sys.stdout.flush()

            self._svc_name_ = args[0]
            self._svc_display_name_ = args[0]

            ServiceFramework.__init__(self, args)

            name = args[0][9:]
            print "Create Program %s" % name ; sys.stdout.flush()
            self.program = Program(name)

            self.program.log_to_daemonlog()

            sys.stdout = sys.stderr = self.logf = self.program._log_stream

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
        self.logf.write('%s:%s\n' % (self._svc_name_, msg))
        self.logf.flush()


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

    def start(self):
        self.runflag = True
        while self.runflag:
            self.sleep(10)
            self.log("I'm alive ...")

    def stop(self):
        self.runflag = False
        self.log("I'm done")

    @classmethod
    def windows_process_manager(cls, startall=True):
        pass

    BUFFER_SIZE = 1024

    def named_pipe_reader(self):
        full_name = r'\\.\pipe\chalmers'

        pipeHandle = CreateNamedPipe(full_name,
            PIPE_ACCESS_DUPLEX,
            PIPE_TYPE_MESSAGE | PIPE_WAIT,
            PIPE_UNLIMITED_INSTANCES, self.BUFFER_SIZE, self.BUFFER_SIZE,
            300, None)

        while 1:
            ConnectNamedPipe(pipeHandle, None)

            _, msg = ReadFile(pipeHandle, self.BUFFER_SIZE)
            msg = msg.split()
            if msg and msg[0]:
                method = getattr(self, 'action_%s' % msg[0], None)
                if method:
                    try:
                        method(*msg[1:])
                    except:
                        WriteFile(pipeHandle, "Error: method raised exception")
                    else:
                        WriteFile(pipeHandle, "ok")
                else:
                    WriteFile(pipeHandle, "Error: bad action")
            else:
                WriteFile(pipeHandle, "Error: bad action")
                log.error("Got empty message from named pipe")

            DisconnectNamedPipe(pipeHandle)


service_path = '%s.%s' % (os.path.splitext(__file__)[0], ChalmersService.__name__)
