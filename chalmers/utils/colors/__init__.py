import os
if os.name == 'nt':
    from .nt import NTColor as color
else:
    from .posix import PosixColor as color
