'''
Start a program.  
The program must be defined with the chalmers 'run' command first

example:

    chalmers start server1
'''
from __future__ import unicode_literals, print_function

from argparse import RawDescriptionHelpFormatter
import logging
import sys

from chalmers.program import Program
from clyent import print_colors
from chalmers import errors
import time


log = logging.getLogger('chalmers.start')


def main(args):

    if args.all:
        programs = list(Program.find_for_user())
        programs = [p for p in programs if not p.is_paused]
    else:
        programs = [Program(name) for name in args.names]

    print("Starting programs %s" % ', '.join([p.name for p in programs]))
    print()
    if args.daemon:
        for prog in programs:
            if not prog.is_running:
                prog.start(args.daemon)

        for prog in programs:
            print("Starting program %-25s ... " % (prog.name[:25]), end='')
            sys.stdout.flush()
            err = prog.wait_for_start()
            if err:
                print_colors('[{=ERROR!c:red} ]')
            else:

                print_colors('[  {=OK!c:green}  ]')

    else:
        if len(programs) != 1:
            raise errors.ChalmersError("start currently only supports running one program in -w/--no-daemon mode")
        prog = programs[0]
        prog.pipe_output = True
        prog.start(daemon=False)


def restart_main(args):


    if args.all:
        programs = Program.find_for_user()
        programs = [prog for prog in programs if not prog.is_paused]
    else:
        programs = [Program(name) for name in args.names]
    if not (args.all or args.names):
        raise errors.ChalmersError("Must specify at least one program to restart")

    if len(programs) == 0:
        log.warn("No programs to restart")
        return

    for prog in programs:

        sys.stdout.flush()

        if prog.is_running:
            print("Stop program %-25s ... " % (prog.name[:25]), end='')
            try:
                prog.stop()
            except errors.StateError:
                print_colors('[  {=ERROR!c:red}  ]')

            print_colors('[  {=OK!c:green}  ]')

    time.sleep(.5)

    for prog in programs:
        prog.start()

    for prog in programs:
        print("Starting program %-25s ... " % (prog.name[:25]), end='')
        sys.stdout.flush()
        err = prog.wait_for_start()
        if err:
            print_colors('[{=ERROR!c:red} ]')
        else:

            print_colors('[  {=OK!c:green}  ]')



def add_parser(subparsers):
    parser = subparsers.add_parser('start',
                                      help='Start a program',
                                      description=__doc__,
                                      formatter_class=RawDescriptionHelpFormatter)

    parser.add_argument('names', nargs='*', metavar='PROG',
                        help='Names of the programs to start')
    parser.add_argument('-w', '--wait', '--no-daemon', action='store_false', dest='daemon',
                        help='Wait for program to exit')
    parser.add_argument('-d', '--daemon', action='store_true', dest='daemon', default=True,
                        help='Run program as daemon')
    parser.add_argument('-a', '--all', action='store_true',
                        help='start all programs')

    parser.set_defaults(main=main)

    parser = subparsers.add_parser('restart',
                                      help='Restart a program',
                                      description=__doc__)

    parser.add_argument('names', nargs='*', metavar='PROG',
                        help='Names of the programs to start')
    parser.add_argument('-a', '--all', action='store_true',
                        help='start all programs')

    parser.set_defaults(main=restart_main)
