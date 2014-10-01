'''
Start a program manager that will track and manager chalmers programs

'''

from __future__ import unicode_literals, print_function

from argparse import RawDescriptionHelpFormatter
import logging
import time
from chalmers.event_dispatcher import send_action
from chalmers.program_manager import ProgramManager
from chalmers import errors


log = logging.getLogger('chalmers.manager')

def main(args):

    mgr = ProgramManager(use_color=args.color)

    if args.is_running:
        try:
            result = mgr.send("ping")
        except errors.ChalmersError:
            log.info("Manager is NOT running")
        else:
            log.info("Manager is running with pid %s" % result)
        return
    if args.shutdown:
        result = mgr.send("exitloop")
        log.info("Manager is shutting down")
        return
    log.info("Managing processes")


    try: 
        result = mgr.send("ping")
    except errors.ChalmersError:
        pass
    else:
        raise errors.ChalmersError("An instance of chalmers manager is already running (pid: %s)" % result)

    mgr.start_all()
    mgr.start_listener()

    #Workaround so keyboard interupt works on win32
    try:
        while mgr.is_listening:
            time.sleep(1)
    except BaseException as err:
        mgr.send('exitloop')
        raise

    print("Finished manager")



def add_parser(subparsers):
    parser = subparsers.add_parser('manager',
                                   help='Manage Chalmers programs',
                                   description=__doc__,
                                   formatter_class=RawDescriptionHelpFormatter)

    parser.add_argument("--shutdown", action='store_true',
                help="Exit manager")
    parser.add_argument("--is-running", action='store_true',
                help="Check if the manager is running")
    parser.set_defaults(main=main)
