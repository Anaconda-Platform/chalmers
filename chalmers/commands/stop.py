'''
Pause program, this program will not be started
when chalmers start -a is run
'''
from __future__ import unicode_literals, print_function
from chalmers.program import Program
import logging
from chalmers import errors

log = logging.getLogger('chalmers.stop')

def main(args):

    prog = Program(args.name)
    log.info("Stopping program %s" % (args.name))
    exit_status = prog.stop()
    log.debug("Program stopped with status %s" % exit_status)
    prog.reload()
    log.info(prog.raw_data.get('exit_message', 'Stopped'))


def pause_main(args):
    prog = Program(args.name)
    log.info("Pausing program %s" % (args.name))
    if prog.is_running:
        raise errors.ChalmersError("Please stop program before pausing")

    prog.update_state(paused=True)


def add_parser(subparsers):
    parser = subparsers.add_parser('stop',
                                   help='Stop running a command',
                                   description=__doc__)

    parser.add_argument('name')

    parser.set_defaults(main=main)

    parser = subparsers.add_parser('pause',
                                      help='Pause program',
                                      description=__doc__)

    parser.add_argument('name')

    parser.set_defaults(main=pause_main)
