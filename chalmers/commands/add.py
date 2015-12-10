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


def main(args):

    if args.cmd and args.command:
        raise errors.ChalmersError('Unknow arguments %r' % args.command)
    elif not (args.cmd or args.command):
        raise errors.ChalmersError('Must specify a command to add')
    if args.cmd:
        args.command = args.cmd

    if not args.name:
        args.name = args.command[0]

    env = {}
    for env_var in args.save_env:
        if env_var in os.environ:
            env[env_var] = os.environ[env_var]
        else:
            log.warn("Environment variable %s does not exist (from -e/--save-env)" % env_var)

    program = Program.add(
        args.name, args.command,
        paused=args.paused, cwd=args.cwd,
        stdout=args.stdout, stderr=args.stderr,
        daemon_log=args.daemon_log, redirect_stderr=args.redirect_stderr,
        env=env
    )

    log.info('Added program {args.name}'.format(args=args))

    if args.run_now:
        log.info('Running program {args.name}'.format(args=args))
        program.start(daemon=not args.wait)


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

    parser.add_argument('-w', '--wait', action='store_true', default=False, dest='wait',
                       help="Wait until program exits to return (default: %(default)s) (--run-now is implyed)")

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
