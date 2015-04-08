
import os, platform

if os.name == 'nt':
    from nt_service import install, uninstall, status
elif platform.system() == 'Darwin':
    from darwin_service import install, uninstall, status
else:
    from posix_service import install, uninstall, status



