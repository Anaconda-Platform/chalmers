'''
Pause program, this program will not be started
when chalmers start -a is run
'''
from __future__ import unicode_literals, print_function
from chalmers.program import Program
import logging
from chalmers import errors
import sys

log = logging.getLogger('chalmers.stop')

def main(args):

    if args.all:
        programs = Program.find_for_user()
    else:
        programs = [Program(name) for name in args.names]

    for prog in programs:
        if prog.is_running:
            print("Stopping program %s ..." % prog.name, end=''); sys.stdout.flush()
            try:
                prog.stop()
            except errors.StateError as err:
                log.error(err.message)
            else:
                print("stopped ")
        else:
            print("Program %s is already stopped" % prog.name)

def pause_main(args):

    if args.all:
        programs = Program.find_for_user()
    else:
        programs = [Program(name) for name in args.names]

    for prog in programs:
        log.info("Pausing program %s" % (prog.name))
        if prog.is_running:
            log.warn("%s is running and will not restart on system reboot" % (prog.name))

        prog.update_state(paused=True)

def unpause_main(args):

    if args.all:
        programs = Program.find_for_user()
    else:
        programs = [Program(name) for name in args.names]

    for prog in programs:
        log.info("Unpausing program %s" % (prog.name))
        prog.update_state(paused=False)
        if not prog.is_running:
            log.warn("%s is not running and will start on system reboot" % (prog.name))


def add_parser(subparsers):
    parser = subparsers.add_parser('stop',
                                   help='Stop running a command',
                                   description=__doc__)

    parser.add_argument('names', nargs='*', metavar='PROG')
    parser.add_argument('-a', '--all', action='store_true')
    parser.set_defaults(main=main)

    parser = subparsers.add_parser('pause',
                                      help='Pause program (don\'t run on system boot)',
                                      description=__doc__)

    parser.add_argument('names', nargs='*', metavar='PROG')
    parser.add_argument('-a', '--all', action='store_true')

    parser.set_defaults(main=pause_main)

    parser = subparsers.add_parser('unpause',
                                      help='Unpause program (run on system boot)',
                                      description=__doc__)

    parser.add_argument('names', nargs='*', metavar='PROG')
    parser.add_argument('-a', '--all', action='store_true')

    parser.set_defaults(main=unpause_main)
