"""
chalmers.service selects the correct service for the platform on import
"""
from __future__ import absolute_import

import os, platform

if os.name == 'nt':

    from .win32_local_service import Win32LocalService
    from .win32_system_service import Win32SystemService

    def Service(target_user):
        "Slecet service instance based on target user"
        if target_user is False:
            return Win32LocalService(target_user)
        else:
            return Win32SystemService(target_user)

elif platform.system() == 'Darwin':
    from .darwin_service import DarwinService as Service
else:
    from .posix_service import PosixService as Service

