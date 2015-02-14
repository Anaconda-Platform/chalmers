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

#         logger = logging.getLogger('chalmers')
#         logger.setLevel(logging.INFO)
#
#         logfile = os.path.join(dirs.user_log_dir, 'service.log')
#
#         hndlr = RotatingFileHandler(logfile, maxBytes=10 * (1024 ** 2), backupCount=5,)
#         hndlr.setLevel(logging.INFO)
#         fmt = logging.Formatter("[%(asctime)s] %(message)s")
#         hndlr.setFormatter(fmt)
#         logger.addHandler(hndlr)
#
#         sys.excepthook = log_unhandled_exception(logger)
#
#         self.mgr = mgr = ProgramManager(use_color=False, setup_logging=False)
#         mgr.start_all()
#         mgr.listen()

    def stop(self):
        pass
#         self.log("Stop Called")
#         for prog in Program.find_for_user():
#             if prog.is_running:
#                 self.log("Stopping program %s" % prog.name)
#                 prog.stop()
#
#         self.log("Sending chalmers manager exit signal")
#         send_action(ProgramManager.NAME, "exitloop")


