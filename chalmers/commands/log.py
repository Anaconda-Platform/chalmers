'''
Show log output of program:

To show the stdout of a run::

    chalmers log server1

To show the chalmers program control log, run::

    chalmers log server1 -3

To show the global chalmers deamon log run::

    chalmers log


You can allso  follow a file (like `tail -f`)

    chalmers log -f
'''

from __future__ import unicode_literals, print_function

from argparse import RawDescriptionHelpFormatter
import logging
import os
import sys
import time

from chalmers import config
from chalmers.program import Program


log = logging.getLogger('chalmers.log')

def main(args):
    if args.name:
        prog = Program(args.name)

        logfile = prog.data.get(args.logfile)
    else:
        logfile = config.main_logfile()
        prog = None


    if args.showfile:
        print(logfile)
        return
    if args.rm:
        if os.path.isfile(logfile):
            log.info("Removing log file '%s'" % logfile)
            os.unlink(logfile)
        else:
            log.warn("File '%s' does not exist" % logfile)
        return

    if logfile is None:
        log.warn("The logfile for key '%s' does not exist" % args.logfile)
        return

    with open(logfile) as fd:
        if args.n:
            lines = fd.readlines()
            if args.n > 0:
                lines = lines[:args.n]
            else:
                lines = lines[args.n:]

            sys.stdout.write(''.join(lines))

        else:
            sys.stdout.write(fd.read())

        while args.append and (not prog or prog and prog.is_running):
            pos = fd.tell()
            if pos < os.fstat(fd.fileno()).st_size:
                fd.seek(pos)
                sys.stdout.write(fd.read())
            else:
                time.sleep(1)


def add_parser(subparsers):
    parser = subparsers.add_parser('log',
                                      help='Show program output',
                                      description=__doc__,
                                      formatter_class=RawDescriptionHelpFormatter)

    parser.add_argument('name', nargs='?')
    parser.add_argument('-f', action='store_true', dest='append',
                       help='The -f option causes log to not stop when end of file is reached, '
                            'but rather to wait for additional data to be appended')

    parser.add_argument('--tail', type=lambda arg:-int(arg), dest='n', metavar='N',
                        default=-10,
                       help='Tail lines at end of file (default: %(default)s)',)
    parser.add_argument('--head', type=int, dest='n', metavar='N',
                       help='Print only first lines of the file')

    parser.add_argument('--showfile', action='store_true',
                       help='Print the name of the logfile')
    parser.add_argument('--rm', '--remove', action='store_true',
                       help='Remove the logfile')

    group = parser.add_mutually_exclusive_group()
    group.add_argument('-1', '--stdout', action='store_const', const='stdout', dest='logfile',
                       default='stdout',
                       help='Show program stdout')
    group.add_argument('-2', '--stderr', action='store_const', const='stderr', dest='logfile',
                       help='Show program stderr')
    group.add_argument('-3', '--daemon', action='store_const', const='daemon_log', dest='logfile',
                       help='Show program manager log')

    parser.set_defaults(main=main)
