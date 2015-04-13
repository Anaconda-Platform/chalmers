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
from chalmers.utils import cli
from chalmers.utils.mutiplex_io_pool import MultiPlexIOPool
import os


log = logging.getLogger('chalmers.start')


def main(args):

    programs = cli.select_programs(args, filter_paused=True)

    programs = cli.filter_programs(programs, lambda p: p.is_running,
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
        pool = MultiPlexIOPool(stream=args.stream, use_color=args.color and os.name == 'posix')

        for prog in programs:
            pool.append(prog)

        pool.join()


def restart_main(args):

    programs = cli.select_programs(args, filter_paused=True)

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

    cli.add_selection_group(parser)

    parser.add_argument('-w', '--wait', '--no-daemon', action='store_false', dest='daemon',
                        help='Wait for program to exit')
    parser.add_argument('-d', '--daemon', action='store_true', dest='daemon', default=True,
                        help='Run program as daemon')
    parser.add_argument('--stream', '--io', action='store_true', default=sys.stdout.isatty(),
                        help='Multiplex stdout of programs to stdout')
    parser.add_argument('--no-stream', action='store_false', dest='stream',
                        help='Don\'t pip stdout of programs to stdout')

    parser.set_defaults(main=main)

    parser = subparsers.add_parser('restart',
                                      help='Restart a program',
                                      description=__doc__,
                                      formatter_class=RawDescriptionHelpFormatter)

    cli.add_selection_group(parser)

    parser.set_defaults(main=restart_main)
