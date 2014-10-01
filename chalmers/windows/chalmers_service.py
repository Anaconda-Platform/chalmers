import logging

from chalmers.event_dispatcher import send_action
from chalmers.program import Program
from chalmers.program_manager import ProgramManager
from chalmers.utils.logutil import setup_logging
from chalmers.windows.service_base import WindowsService


class ChalmersService(WindowsService):
    """
    Run the chalmers manager process as a windows service
    """
    def start(self):

        setup_logging(logging.INFO, False, 'service.log')
        self.mgr = mgr = ProgramManager(use_color=False)
        mgr.start_all()
        mgr.listen()

    def stop(self):

        self.log("Stop Called")
        for prog in Program.find_for_user():
            if prog.is_running:
                self.log("Stopping program %s" % prog.name)
                prog.stop()

        self.log("Sending chalmers manager exit signal")
        send_action(ProgramManager.NAME, "exitloop")


