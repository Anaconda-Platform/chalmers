'''
Add a program without running it

eg:
    chalmers add --name server1 -- python /path/to/myserver.py
or:
    chalmers add --name server1 -c "python /path/to/myserver.py"
    
    
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
    elif not (args.cmd or args.command):
        raise errors.ChalmersError('Must specify a command to add')
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
    env = {}
    for env_var in args.save_env:
        if env_var in os.environ:
            env[env_var] = os.environ[env_var]
        else:
            log.warn("Environment variable %s does not exist (from -e/--save-env)" % env_var)

    definition = {
                    'name': args.name,
                    'command': args.command,
                    'cwd': os.path.abspath(args.cwd),
                    'env': env,
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
        prog.pipe_output = not args.daemon
        prog.start(daemon=args.daemon)

    prog.save()
    log.info('Added program {args.name}'.format(args=args))

def add_parser(subparsers):
    parser = subparsers.add_parser('add',
                                      help='Add a command to run later',
                                      description=__doc__,
                                      formatter_class=RawDescriptionHelpFormatter
                                      )
    #===============================================================================
    #
    #===============================================================================
    group = parser.add_argument_group('Starting State') \
                  .add_mutually_exclusive_group()

    group.add_argument('--paused', action='store_true', dest='paused',
                       help="don't start program automatically at system start", default=True)
    group.add_argument('--un-paused', action='store_false', dest='paused',
                       help="Start program automatically at system start")

    #===========================================================================
    #
    #===========================================================================
    group = parser.add_argument_group('Process Output:')
    group.add_argument('--stdout',
                       help='Filename to log stdout to')
    group.add_argument('--stderr',
                       help='Filename to log stderr to')
    group.add_argument('--daemon-log',
                       help='Filename to log meta information about this process to')
    group.add_argument('--redirect-stderr', action='store_true', default=True,
                       dest='redirect_stderr',
                       help='Store stdout and stderr in the same log file (default: %(default)s)')
    group.add_argument('--dont-redirect-stderr', action='store_false',
                       dest='redirect_stderr',
                       help='Store stdout and stderr in seporate log files')
    #===========================================================================
    #
    #===========================================================================
    parser.add_argument('-n', '--name',
                        help='Set the name of this program for future chalmers commands')

    parser.add_argument('--cwd', default=os.curdir,
                        help='Set working directory of the program (default: %(default)s)')

    parser.add_argument('command', nargs='*', metavar='COMMAND',
                        help='Command to run')

    split = lambda item: shlex.split(item, posix=os.name == 'posix')

    parser.add_argument('-c', metavar='COMMAND', type=split, dest='cmd',
                        help='Command to run')

    parser.add_argument('-e', '--save-env', metavar='ENV_VAR', action='append', default=[],
                        help='Save a current environment variable to be run( Eg. --save-env PATH)')

    parser.set_defaults(main=main, state='pause')
