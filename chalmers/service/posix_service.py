"""
Linux services, this module checks the existence of linux command line 
programs on import

 * systemd_service
 * upstart_service
 * sysv_service
 * cron_service

In that order  
"""
from __future__ import unicode_literals, print_function

# Fix for AWS Linux
import platform
platform._supported_dists += ('system',)

import logging

from . import cron_service, sysv_service, upstart_service, systemd_service


log = logging.getLogger('chalmers.service')

if systemd_service.check():
    PosixService = systemd_service.SystemdService
elif sysv_service.check():
    PosixService = sysv_service.SysVService
elif upstart_service.check():
    PosixService = upstart_service.UpstartService
else:
    PosixService = cron_service.CronService

