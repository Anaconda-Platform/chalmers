"""
Chalmers error classes
"""
from clyent.errors import ClyentError

class ChalmersError(ClyentError):
    """
    Generic error that will hide the traceback
    unless --show-traceback is given

    the 'message' must then always be immediately obvious
    to the end user
    """
    def __init__(self, *args, **kwargs):
        self.message = args[0] if args else None
        ClyentError.__init__(self, *args, **kwargs)

class ProgramNotFound(ChalmersError):
    'No program definition found on disk'
    pass

class StateError(ChalmersError):
    pass

class ConnectionError(ChalmersError):
    pass

class StopProcess(Exception):
    'called to signal a process should exit'
