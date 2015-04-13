'''
Stop a program from running:

    chalmers stop server1

Stopping a program will send a signal to the program. The signal can be set beforehand by:

    chalmers set server1 stopsignal=SIGTERM
 
Stop differs from off, off will not stop the program.
When off a program will not be started at system boot (or `start --all`)

When a program is *on* it will still start at system boot
even if you manually stop it before a reboot.
'''

from __future__ import unicode_literals, print_function

from argparse import RawDescriptionHelpFormatter
import logging
import sys

from clyent import print_colors

from chalmers import errors
from chalmers.utils import cli


log = logging.getLogger('chalmers.stop')

def main(args):

    programs = cli.select_programs(args, filter_paused=False, force=args.force)

    programs = cli.filter_programs(programs, lambda p: not p.is_running, 'Stopping', 'stopped')
    if not programs:
        return
    for prog in programs:
        if prog.is_running:
            print("Stopping program %-25s ... " % prog.name[:25], end=''); sys.stdout.flush()
            try:
                prog.stop(args.force)
            except errors.StateError as err:
                log.error(err.message)
            except errors.ConnectionError as err:
                print_colors("[  {=ERROR!c:red}  ] %s (use --force to force stop the program)" % err.message)
            else:
                print_colors("[  {=OK!c:green}  ]")
        else:
            print_colors("Program is already stopped: %-25s " % prog.name[:25], "[{=STOPPED!c:yello} ]")

def pause_main(args):

    programs = cli.select_programs(args, filter_paused=False)
    programs = cli.filter_programs(programs, lambda p: p.is_paused, 'Pausing', 'paused')
    if not programs:
        return

    for prog in programs:
        log.info("Pausing program %s" % (prog.name))
        if prog.is_running:
            log.warn("%s is running and will not restart on system reboot" % (prog.name))

        prog.state.update(paused=True)

def unpause_main(args):

    programs = cli.select_programs(args, filter_paused=False)
    programs = cli.filter_programs(programs, lambda p: not p.is_paused, 'Unpausing', 'unpaused')

    if not programs:
        return

    for prog in programs:
        log.info("Unpausing program %s" % (prog.name))
        prog.state.update(paused=False)
        if not prog.is_running:
            log.warning("%s is not running and will start on next system boot" % (prog.name))


def add_parser(subparsers):
    parser = subparsers.add_parser('stop',
                                   help='Stop running a command',
                                   description=__doc__,
                                   formatter_class=RawDescriptionHelpFormatter)

    cli.add_selection_group(parser)
    parser.add_argument('--force', action='store_true',
                        help='Force kill a program (stopsignal will be ignored)'
                        )

    parser.set_defaults(main=main)

    parser = subparsers.add_parser('off',
                                   help='Don\'t run a program on system boot or `chalmers start --all`',
                                   description=__doc__,
                                   formatter_class=RawDescriptionHelpFormatter)

    cli.add_selection_group(parser)

    parser.set_defaults(main=pause_main)

    parser = subparsers.add_parser('on',
                                   help='Run a program on system boot or `chalmers start --all`',
                                   description=__doc__,
                                   formatter_class=RawDescriptionHelpFormatter)

    cli.add_selection_group(parser)

    parser.set_defaults(main=unpause_main)
