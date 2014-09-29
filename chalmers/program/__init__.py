import os 

if os.name == 'nt':
   from .nt import Program
else: # posix
   from .posix import Program