"""
chalmers.service selects the correct service for the platform on import
"""
from __future__ import absolute_import

import os, platform

if os.name == 'nt':

    from .win32_local_service import Win32LocalService as LocalService
    from .win32_system_service import Win32SystemService as SystemService

    def Service(target_user):
        "Slecet service instance based on target user"
        if target_user is False:
            return LocalService(target_user)
        else:
            return SystemService(target_user)

elif platform.system() == 'Darwin':
    from .darwin_service import DarwinService as SystemService
    LocalService = SystemService
else:
    from .posix_service import PosixSystemService as SystemService, PosixLocalService as LocalService

