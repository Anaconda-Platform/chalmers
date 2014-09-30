import getpass
import logging
from os.path import abspath
import sys

from chalmers.scripts import service as service_script
import win32api, win32serviceutil, win32service


log = logging.getLogger(__name__)

def InstallService(serviceName, displayName, startType=win32service.SERVICE_DEMAND_START,
                    serviceDeps=None,
                    errorControl=win32service.SERVICE_ERROR_NORMAL,
                    userName=None, password=None,
                    description=None):
    serviceType = win32service.SERVICE_WIN32_OWN_PROCESS

    script = abspath(service_script.__file__)
    commandLine = "%s %s" % (sys.executable, script)

    hscm = win32service.OpenSCManager(None, None, win32service.SC_MANAGER_ALL_ACCESS)

    try:
        hs = win32service.CreateService(hscm,
                                serviceName,
                                displayName,
                                win32service.SERVICE_ALL_ACCESS,  # desired access
                    serviceType,  # service type
                    startType,
                    errorControl,  # error control type
                    commandLine,
                    None,
                    0,
                    serviceDeps,
                    userName,
                    password)

        if description is not None:
            try:
                win32service.ChangeServiceConfig2(hs, win32service.SERVICE_CONFIG_DESCRIPTION, description)
            except NotImplementedError:
                pass  # # ChangeServiceConfig2 and description do not exist on NT

        win32service.CloseServiceHandle(hs)
    finally:
        win32service.CloseServiceHandle(hscm)

def get_service_name(userName):
    "Return the service name for the given user"
    simpleUserName = userName.rsplit('\\', 1)[-1]
    svc_name = 'chalmers:manager:%s' % simpleUserName
    return svc_name

def is_running(userName=getpass.getuser()):
    "Test if the chalmers sevice is running for 'userName'"
    svc_name = get_service_name(userName)
    try:
        status = win32serviceutil.QueryServiceStatus(svc_name)
    except win32api.error:
        return False
    return status[1] == win32service.SERVICE_RUNNING

def is_installed(userName=getpass.getuser()):
    "Test if the chalmers sevice is installed for 'userName'"
    svc_name = get_service_name(userName)
    try:
        win32serviceutil.QueryServiceStatus(svc_name)
        return True
    except win32api.error:
        return False

def instart(userName, password):
    ''' Install and  Start (auto) a the chalmers service
    '''

    simpleUserName = userName.rsplit('\\', 1)[-1]
    svc_name = get_service_name(userName)
    display_name = 'Chalmers service manager for user %s' % simpleUserName

    win32api.SetConsoleCtrlHandler(lambda x: True, True)

    InstallService(
        svc_name,
        display_name,
        startType=win32service.SERVICE_AUTO_START,
        userName=userName,
        password=password,
    )

    log.info('Install OK')
    win32serviceutil.StartService(svc_name)
    log.info('Start OK')


