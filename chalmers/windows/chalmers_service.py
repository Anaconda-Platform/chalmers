"""
Windows win32service class overloaded to run chalmers processes

This service will exit almost immediatly, all processes are
'daemonized' (win32 compatible) and the service will exit while
the processes are still running
"""
from chalmers.program import Program
from chalmers.windows.service_base import WindowsService


class ChalmersService(WindowsService):
    """
    Run the chalmers manager process as a windows service
    """
    def start(self):

        programs = list(Program.find_for_user())
        programs = [p for p in programs if not p.is_paused]

        for prog in programs:
            if not prog.is_running:
                prog.start(True)

    def stop(self):
        pass
