'''
'''
from __future__ import unicode_literals, print_function
import logging
from chalmers.program import Program
from chalmers import errors

log = logging.getLogger('chalmers.start')

def main(args):

    if args.all:
        if not args.daemon:
            raise errors.ChalmersError("Option --all conflicts with option -w/--wait/--no-daemin")

        print("Starting all programs")
        for prog in Program.find_for_user():
            if prog.is_paused:
                print(" - Program %s is paused" % prog.name)
            elif not prog.is_running:
                print(" + Starting program %s" % prog.name)
                prog.start(daemon=True)
            else:
                print(" - Programs %s is already running" % prog.name)
    else:
        prog = Program(args.name)
        print("Starting program %s" % prog.name)
        prog.start(daemon=args.daemon)
        if args.daemon:
            print("args.daemon")
            print("prog.reload_state()", prog.state_filename)
            prog.reload_state()
            print("prog.state", prog.state)
        else:
            print("Wait!")


def add_parser(subparsers):
    parser = subparsers.add_parser('start',
                                      help='Start a command running',
                                      description=__doc__)

    parser.add_argument('name', nargs='?',
                        help='Name of the program to run')
    parser.add_argument('-w', '--wait', '--no-daemon', action='store_false', dest='daemon',
                        help='Wait for program to exit')
    parser.add_argument('-d', '--daemon', action='store_true', dest='daemon', default=True,
                        help='Run program as daemon')
    parser.add_argument('-a', '--all', action='store_true',
                        help='start all programs')

    parser.set_defaults(main=main)
