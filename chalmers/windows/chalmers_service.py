import logging

from clyent.logs import setup_logging

from chalmers.event_dispatcher import send_action
from chalmers.program import Program
from chalmers.program_manager import ProgramManager
from chalmers.windows.service_base import WindowsService
from build.lib.chalmers.config import dirs
import os


class ChalmersService(WindowsService):
    """
    Run the chalmers manager process as a windows service
    """
    def start(self):
        logger = logging.getLogger('chalmers')
        logfile = os.path.join(dirs.user_log_dir, 'service.log')
        setup_logging(logger, logging.INFO, False, logfile, True)
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


