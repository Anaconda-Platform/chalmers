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

import logging
import platform
import sys

from . import cron_service, sysv_service, upstart_service, systemd_service
from chalmers import errors


# Fix for AWS Linux
if sys.version_info.major == 3:
    system_dist = ('system',)
else:
    system_dist = (b'system',)

platform._supported_dists += system_dist


log = logging.getLogger('chalmers.service')

class NoPosixSystemService(object):

    def __init__(self, target_user=None):
        supported_dists = platform._supported_dists + system_dist
        linux = platform.linux_distribution(supported_dists=supported_dists)
        raise errors.ChalmersError("Could not detect system service for platform %s (tried systemd, sysv init and upstart)" % linux[0])

if systemd_service.check():
    PosixSystemService = systemd_service.SystemdService
elif sysv_service.check():
    PosixSystemService = sysv_service.SysVService
elif upstart_service.check():
    PosixSystemService = upstart_service.UpstartService
else:
    PosixSystemService = NoPosixSystemService

PosixLocalService = cron_service.CronService

