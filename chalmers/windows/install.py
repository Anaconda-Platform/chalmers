"""
Install a win32 service using the win32api
"""
import getpass
import logging
import os
from os.path import abspath
import sys

from pywintypes import error as Win32Error
import win32api, win32serviceutil, win32service

from chalmers import errors
from chalmers.scripts import service as service_script

log = logging.getLogger(__name__)

ERR_SERVICE_EXISTS = 1073

def InstallService(serviceName, displayName, startType=win32service.SERVICE_DEMAND_START,
                    serviceDeps=None,
                    errorControl=win32service.SERVICE_ERROR_NORMAL,
                    userName=None, password=None,
                    description=None):
    """
    This is a copy of a more advanced usecase.
    For chalmers serviceName and displayName are required and the
    defaults should be sufficient
    """
    serviceType = win32service.SERVICE_WIN32_OWN_PROCESS

    script = abspath(service_script.__file__)

    if script.endswith('.pyc') or script.endswith('.pyo'):
        script = script[:-1]

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
                win32service.ChangeServiceConfig2(hs,
                                                  win32service.SERVICE_CONFIG_DESCRIPTION,
                                                  description)
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
    try:
        InstallService(
            svc_name,
            display_name,
            startType=win32service.SERVICE_AUTO_START,
            userName=userName,
            password=password,
        )

    except Win32Error as err:
        if err.args[0] != ERR_SERVICE_EXISTS:
            raise
        log.warn('Chalmers service %s is already installed' % svc_name)
    else:
        log.info('Installed chalmers service %s to windows services' % svc_name)

    try:
        win32serviceutil.StartService(svc_name)
    except Win32Error as err:
        log.error('StartService: %s' % err.args[2])
        if err.args[0] == 1069:
            log.error("This is usually a password error, please uninstall the service and retry")
            log.error(" *OR*")
            log.error("Run the command:\n\tsc config %s password= \"pass\"\nsc start %s" %
                      (svc_name, svc_name))
            log.error(" *OR*")
            log.error("Open the 'Services' application and edit it there")
        else:
            AllUsersProfile = os.environ.get('AllUsersProfile', 'C:\\ProgramData')
            logfile = os.path.join(AllUsersProfile, '%s-chalmers-service-log.txt' %
                                   userName.rsplit('\\', 1)[-1])
            log.error("Could not start the chalmers windows service for user %s" %
                      userName)
            log.error('Check the logfile "%s" for more details' % logfile)
    else:
        log.info('Start OK')


