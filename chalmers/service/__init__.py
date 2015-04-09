
import os, platform

if os.name == 'nt':
    from nt_service import NTService as Service
elif platform.system() == 'Darwin':
    from darwin_service import DarwinService as Service
else:
    from posix_service import PosixService as Service



