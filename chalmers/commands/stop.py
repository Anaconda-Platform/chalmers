'''
Stop/Pause/Unpause a program

Stopping a program will send a signal to the program. The signal can be set by:

    chalmers set server1 stopsignal=SIGTERM
 
When paused, a program will not be started at system boot 
'''

from __future__ import unicode_literals, print_function

from argparse import RawDescriptionHelpFormatter
import logging
import sys

from clyent import print_colors

from chalmers import errors
from chalmers.utils.cli import add_selection_group, select_programs, \
    filter_programs


log = logging.getLogger('chalmers.stop')

def main(args):

    programs = select_programs(args, filter_paused=False)

    programs = filter_programs(programs, lambda p: not p.is_running, 'Stopping', 'stopped')
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

    programs = select_programs(args, filter_paused=False)
    programs = filter_programs(programs, lambda p: p.is_paused, 'Pausing', 'paused')
    if not programs:
        return

    for prog in programs:
        log.info("Pausing program %s" % (prog.name))
        if prog.is_running:
            log.warn("%s is running and will not restart on system reboot" % (prog.name))

        prog.state.update(paused=True)

def unpause_main(args):

    programs = select_programs(args, filter_paused=False)
    programs = filter_programs(programs, lambda p: not p.is_paused, 'Unpausing', 'unpaused')

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

    add_selection_group(parser)
    parser.add_argument('--force', action='store_true',
                        help='Force kill a program (stopsignal will be ignored)'
                        )

    parser.set_defaults(main=main)

    parser = subparsers.add_parser('pause',
                                      help='Pause program (don\'t run on system boot)',
                                      description=__doc__,
                                      formatter_class=RawDescriptionHelpFormatter)

    add_selection_group(parser)

    parser.set_defaults(main=pause_main)

    parser = subparsers.add_parser('unpause',
                                      help='Unpause program (run on system boot)',
                                      description=__doc__,
                                      formatter_class=RawDescriptionHelpFormatter)

    add_selection_group(parser)

    parser.set_defaults(main=unpause_main)
