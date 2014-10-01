'''
Run a program

eg:
    chalmers run --name server1 -- python /path/to/myserver.py
or:
    chalmers run --name server1 -c "python /path/to/myserver.py"
    
    
'''
from __future__ import unicode_literals, print_function

import logging
from os import path
import os

from chalmers import errors
from chalmers.config import dirs
from chalmers.program import Program
from argparse import RawDescriptionHelpFormatter
import shlex


log = logging.getLogger('chalmers.add')

def main(args):

    if args.cmd and args.command:
        raise errors.ChalmersError('Unknow arguments %r' % args.command)
    if args.cmd:
        args.command = args.cmd

    program_dir = path.join(dirs.user_data_dir, 'programs')

    if not args.name:
        args.name = args.command[0]

    if not path.isdir(program_dir):
        os.makedirs(program_dir)

    program_defn = path.join(program_dir, '{args.name}.yaml'.format(args=args))
    if path.isfile(program_defn):
        raise errors.ChalmersError("Program with name '{args.name}' already exists.  \n"
                                   "Use the -n/--name option to change the name or \n"
                                   "Run 'chalmers remove {args.name}' to remove it \n"
                                   "or 'chalmers set' to update the parameters".format(args=args))

    definition = {
                    'name': args.name,
                    'command': args.command,
    }

    if args.stdout:
        definition['stdout'] = args.stdout

    if args.daemon_log:
        definition['daemon_log'] = args.daemon_log

    if args.redirect_stderr is not None:
        definition['redirect_stderr'] = args.redirect_stderr

    if args.stderr is not None:
        definition['stderr'] = args.stderr

    state = {'paused': args.paused}

    prog = Program.create(args.name, definition, state)
    prog.save_state()

    if not args.paused:
        log.info('Starting program {args.name}'.format(args=args))
        prog.start(daemon=args.daemon)

    if args.daemon:
        prog.save()
        log.info('Added program {args.name}'.format(args=args))
    else:
        log.info('Program {args.name} exited'.format(args=args))


def add_parser(subparsers):
    parser = subparsers.add_parser('run',
                                      help='Manage a command to run',
                                      description=__doc__,
                                      formatter_class=RawDescriptionHelpFormatter
                                      )
    #===============================================================================
    #
    #===============================================================================
    group = parser.add_argument_group('Starting State') \
                  .add_mutually_exclusive_group()

    group.add_argument('--start', action='store_false', dest='paused', default=False,
                       help="Start program automatically (default)")
    group.add_argument('--paused', action='store_true', dest='paused',
                       help="don't start program automatically")

    group.add_argument('--daemon', action='store_true', default=True,
                       help="Run command in the background")
    group.add_argument('-w', '--wait', '--no-daemon', action='store_false', dest='daemon',
                       help="Run command in the foreground")
    #===========================================================================
    #
    #===========================================================================
    group = parser.add_argument_group('Process Output:')
    group.add_argument('--stdout')
    group.add_argument('--stderr')
    group.add_argument('--daemon-log')
    group.add_argument('--redirect-stderr', action='store_true')
    #===========================================================================
    #
    #===========================================================================
    parser.add_argument('-n', '--name',
                        help='Set the name of this program for future chalmers commands')
    parser.add_argument('command', nargs='*', metavar='COMMAND',
                        help='Command to run')
    split = lambda item: shlex.split(item, posix=os.name == 'posix')

    parser.add_argument('-c', metavar='COMMAND', type=split, dest='cmd',
                        help='Command to run')
    parser.set_defaults(main=main, state='pause')
