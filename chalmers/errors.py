"""
Chalmers error classes
"""
from clyent.errors import ClyentError

class ChalmersError(ClyentError):
    pass

class ProgramNotFound(ChalmersError):
    pass

class StateError(ChalmersError):
    pass


class ShowHelp(object):
    pass



class StopProcess(Exception):
    pass
