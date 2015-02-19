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
import time

from clyent import print_colors

from chalmers import errors
from chalmers.utils.cli import add_selection_group, select_programs, \
    filter_programs


log = logging.getLogger('chalmers.start')


def main(args):

    programs = select_programs(args, filter_paused=True)

    programs = filter_programs(programs, lambda p: p.is_running,
                               'Starting', 'started', True)

    if args.daemon:
        for prog in programs:
            if not prog.is_running:
                prog.start(args.daemon)

        for prog in programs:
            print("Checking status of program %-25s ... " % (prog.name[:25]), end='')
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

    programs = select_programs(args, filter_paused=True)

    if not (args.all or args.names):
        raise errors.ChalmersError("Must specify at least one program to restart")

    if len(programs):
        print("Restarting programs %s" % ', '.join([p.name for p in programs]))
        print("")
    else:
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
        print("Checking status of program %-25s ... " % (prog.name[:25]), end='')
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

    add_selection_group(parser)

    parser.add_argument('-w', '--wait', '--no-daemon', action='store_false', dest='daemon',
                        help='Wait for program to exit')
    parser.add_argument('-d', '--daemon', action='store_true', dest='daemon', default=True,
                        help='Run program as daemon')

    parser.set_defaults(main=main)

    parser = subparsers.add_parser('restart',
                                      help='Restart a program',
                                      description=__doc__,
                                      formatter_class=RawDescriptionHelpFormatter)

    add_selection_group(parser)

    parser.set_defaults(main=restart_main)
