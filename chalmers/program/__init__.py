import os

if os.name == 'nt':
    from .nt import NTProgram as Program
else:  # posix
    from .posix import PosixProgram as Program
