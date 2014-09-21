'''
'''
from __future__ import unicode_literals, print_function
from chalmers.program import Program
import logging

log = logging.getLogger('chalmers.stop')

def main(args):

    prog = Program(args.name)
    log.info("Stopping program %s" % (args.name))
    exit_status = prog.stop()
    log.debug("Program stopped with status %s" % exit_status)
    prog.reload()
    log.info(prog.raw_data.get('exit_message', 'Stopped'))


def add_parser(subparsers):
    parser = subparsers.add_parser('stop',
                                      help='Stop running a command',
                                      description=__doc__)

    parser.add_argument('name')

    parser.set_defaults(main=main)
