"""
Chalmers error classes
"""
from clyent.errors import ClyentError

class ChalmersError(ClyentError):
    def __init__(self, *args, **kwargs):
        self.message = args[0] if args else None
        ClyentError.__init__(self, *args, **kwargs)

class ProgramNotFound(ChalmersError):
    pass

class StateError(ChalmersError):
    pass

class ConnectionError(ChalmersError):
    pass

class ShowHelp(object):
    pass



class StopProcess(Exception):
    pass
