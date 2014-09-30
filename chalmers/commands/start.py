'''
'''
from __future__ import unicode_literals, print_function

import logging

from chalmers import errors
from chalmers.program import Program
from chalmers.program_manager import ProgramManager


log = logging.getLogger('chalmers.start')


def main(args):

    if args.all:
        programs = list(Program.find_for_user())
    else:
        programs = [Program(name) for name in args.names]

    mgr = ProgramManager()

    for prog in programs:
        mgr.action_start(prog.name)

    for process in mgr.processes:
        process.join()

#     if len(programs) > 1 and not args.daemon:
#         raise errors.ChalmersError("Can not use -w/--wait with multiple programs")
#

def restart_main(args):

    if args.all:
        programs = Program.find_for_user()
    else:
        programs = [Program(name) for name in args.names]

    for prog in programs:
        prog.restart()



def add_parser(subparsers):
    parser = subparsers.add_parser('start',
                                      help='Start a command running',
                                      description=__doc__)

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
