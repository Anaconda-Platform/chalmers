"""
Chalmers error classes
"""

class ChalmersError(Exception):
    pass

class ProgramNotFound(ChalmersError):
    pass

class StateError(ChalmersError):
    pass


class ShowHelp(object):
    pass



class StopProcess(Exception):
    pass
