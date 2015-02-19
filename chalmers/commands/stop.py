'''
Stop/Pause/Unpause a program

Stopping a program will send a signal to the program. The signal can be set by:

    chalmers set server1 stopsignal=SIGTERM
 
When paused, a program will not be started at system boot 
'''

from __future__ import unicode_literals, print_function

from argparse import RawDescriptionHelpFormatter
import logging
import sys

from chalmers import errors
from chalmers.program import Program
from clyent import print_colors

log = logging.getLogger('chalmers.stop')

def main(args):

    if args.all:
        programs = Program.find_for_user()
    else:
        programs = [Program(name) for name in args.names]

    already_stopped_programs = [p.name for p in programs if not p.is_running]
    if already_stopped_programs:
        print("The programs '%s' are already stopped" % "', '".join(already_stopped_programs))

    programs = [p for p in programs if p.is_running]

    if len(programs):
        print("Stopping programs %s" % ', '.join([p.name for p in programs]))
        print("")
    else:
        print("No programs to stop")
        return

    for prog in programs:
        if prog.is_running:
            print("Stopping program %-25s ... " % prog.name[:25], end=''); sys.stdout.flush()
            try:
                prog.stop(args.force)
            except errors.StateError as err:
                log.error(err.message)
            except errors.ConnectionError as err:
                print_colors("[  {=ERROR!c:red}  ] %s (use --force to force stop the program)" % err.message)
            else:
                print_colors("[  {=OK!c:green}  ]")
        else:
            print_colors("Program is already stopped: %-25s " % prog.name[:25], "[{=STOPPED!c:yello} ]")

def pause_main(args):

    if args.all:
        programs = Program.find_for_user()
    else:
        programs = [Program(name) for name in args.names]

    for prog in programs:
        log.info("Pausing program %s" % (prog.name))
        if prog.is_running:
            log.warn("%s is running and will not restart on system reboot" % (prog.name))

        prog.state.update(paused=True)

def unpause_main(args):

    if args.all:
        programs = Program.find_for_user()
    else:
        programs = [Program(name) for name in args.names]

    for prog in programs:
        log.info("Unpausing program %s" % (prog.name))
        prog.state.update(paused=False)
        if not prog.is_running:
            log.warn("%s is not running and will start on system reboot" % (prog.name))


def add_parser(subparsers):
    parser = subparsers.add_parser('stop',
                                   help='Stop running a command',
                                   description=__doc__,
                                   formatter_class=RawDescriptionHelpFormatter)

    parser.add_argument('names', nargs='*', metavar='PROG',
                        help='Name of program')
    parser.add_argument('-a', '--all', action='store_true',
                        help='Select all programs')
    parser.add_argument('--force', action='store_true',
                        help='Force kill a program (stopsignal will be ignored)'
                        )

    parser.set_defaults(main=main)

    parser = subparsers.add_parser('pause',
                                      help='Pause program (don\'t run on system boot)',
                                      description=__doc__,
                                      formatter_class=RawDescriptionHelpFormatter)

    parser.add_argument('names', nargs='*', metavar='PROG',
                        help='Name of program')
    parser.add_argument('-a', '--all', action='store_true',
                        help='Select all programs')

    parser.set_defaults(main=pause_main)

    parser = subparsers.add_parser('unpause',
                                      help='Unpause program (run on system boot)',
                                      description=__doc__,
                                      formatter_class=RawDescriptionHelpFormatter)

    parser.add_argument('names', nargs='*', metavar='PROG',
                        help='Name of program')
    parser.add_argument('-a', '--all', action='store_true',
                        help='Select all programs')

    parser.set_defaults(main=unpause_main)
