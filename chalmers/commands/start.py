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
            if not prog.is_running:
                print("Starting program %s" % prog.name)
                prog.start_async(daemon=args.daemon)
            else:
                print("Programs %s is already running" % prog.name)
    else:
        prog = Program(args.name)
        prog.start_async(daemon=args.daemon)

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
