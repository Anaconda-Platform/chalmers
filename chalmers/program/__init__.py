"""
A program encapsulates all of the actions and functionality need
to operate on and query an underlying process. 
"""

import os

if os.name == 'nt':
    from .nt import NTProgram as Program
else:  # posix
    from .posix import PosixProgram as Program
