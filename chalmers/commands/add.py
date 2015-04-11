'''
Add a program without running it

eg:
    chalmers add --name server1 -- python /path/to/myserver.py
or:
    chalmers add --name server1 -c "python /path/to/myserver.py"

Note that this does not run the program by default. To run your program,

run `chalmers start NAME` or use the run-now option eg. `chalmers add --run-now ...`
 
'''
from __future__ import unicode_literals, print_function

from argparse import RawDescriptionHelpFormatter
import logging
import os
import shlex

from chalmers import errors
from chalmers.program import Program

log = logging.getLogger('chalmers.add')

def create_definition(args):

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

    return definition


def main(args):
    if args.cmd and args.command:
        raise errors.ChalmersError('Unknow arguments %r' % args.command)
    elif not (args.cmd or args.command):
        raise errors.ChalmersError('Must specify a command to add')
    if args.cmd:
        args.command = args.cmd

    if not args.name:
        args.name = args.command[0]

    program = Program(args.name)

    if program.exists():
        raise errors.ChalmersError("Program with name '{args.name}' already exists.  \n"
                                   "Use the -n/--name option to change the name or \n"
                                   "Run 'chalmers remove {args.name}' to remove it \n"
                                   "or 'chalmers set' to update the parameters".format(args=args))

    state = {'paused': args.paused}
    definition = create_definition(args)

    program.raw_data.update(definition)
    program.state.update(state)

    if args.run_now:
        program.start()

    log.info('Added program {args.name}'.format(args=args))

def add_parser(subparsers):
    description = 'Add a command to run'
    parser = subparsers.add_parser('add',
                                   help=description, description=description,
                                   epilog=__doc__,
                                   formatter_class=RawDescriptionHelpFormatter
                                      )
    #===============================================================================
    #
    #===============================================================================
    group = parser.add_argument_group('Starting State') \
                  .add_mutually_exclusive_group()

    group.add_argument('--off', '--paused', action='store_true', dest='paused',
                       help="Don't start program automatically at system start (exclude from `chalmers start --all`)",
                       default=False)
    group.add_argument('--on', '--un-paused', action='store_false', dest='paused',
                       help="Start program automatically at system start (include in `chalmers start --all`)")

    group.add_argument('-r', '--run-now', action='store_true', default=False, dest='run_now',
                       help="Start program Right now (default: %(default)s)")
    group.add_argument('-l', '--dont-run-now', '--run-later', action='store_false', dest='run_now',
                       help="Start the program later with `chalmers start ...`")

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
