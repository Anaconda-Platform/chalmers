'''
'''
from __future__ import unicode_literals, print_function

import logging

from chalmers import errors
from chalmers.program import Program


log = logging.getLogger('chalmers.start')


def main(args):

    if args.all:
        if not args.daemon:
            raise errors.ChalmersError("Option --all conflicts with option -w/--wait/--no-daemin")

        Program.start_all()

    else:
        prog = Program(args.name)
        log.info("Starting program %s (daemon:%s)" % (prog.name, args.daemon))
        prog.start(daemon=args.daemon)


def restart_main(args):
    if args.all:
        if not args.daemon:
            raise errors.ChalmersError("Option --all conflicts with option -w/--wait/--no-daemin")

        Program.start_all()

    else:
        prog = Program(args.name)
        log.info(" - Stopping program %s" % prog.name)
        try:
            prog.stop()
        except errors.StateError:
            log.info(" - Program %s was not running" % prog.name)
        log.info(" + Starting program %s" % prog.name)
        prog.start()



def add_parser(subparsers):
    parser = subparsers.add_parser('start',
                                      help='Start a command running',
                                      description=__doc__)

    parser.add_argument('name', nargs='?',
                        help='Name of the program to start')
    parser.add_argument('-w', '--wait', '--no-daemon', action='store_false', dest='daemon',
                        help='Wait for program to exit')
    parser.add_argument('-d', '--daemon', action='store_true', dest='daemon', default=True,
                        help='Run program as daemon')
    parser.add_argument('-a', '--all', action='store_true',
                        help='start all programs')

    parser = subparsers.add_parser('restart',
                                      help='Restart a program',
                                      description=__doc__)

    parser.add_argument('name', nargs='?',
                        help='Name of the program to restart')
    parser.add_argument('-a', '--all', action='store_true',
                        help='start all programs')

    parser.set_defaults(main=restart_main)
