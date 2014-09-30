from chalmers.windows.service_base import WindowsService
from chalmers.utils.logutil import setup_logging
import logging
from chalmers.program_manager import ProgramManager
from chalmers.program import Program
import os
import sys

class ChalmersService(WindowsService):

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
        send_action("chalmers", "exitloop")

        

service_path = '%s.%s' % (os.path.splitext(__file__)[0], ChalmersService.__name__)
