'''
'''
from __future__ import unicode_literals, print_function
from chalmers.program import Program
import logging

log = logging.getLogger('chalmers.stop')

def main(args):

    proc = Program(args.name)
    log.info("Stopping program %s" % (args.name))
    exit_status = proc.stop()
    log.debug("Program stopped with status %s" % exit_status)
    proc.reload()
    log.info(proc.raw_data.get('exit_message', 'Stopped'))


def add_parser(subparsers):
    parser = subparsers.add_parser('stop',
                                      help='List registered commands',
                                      description=__doc__)

    parser.add_argument('-n', '--name', required=True)

    parser.set_defaults(main=main)
