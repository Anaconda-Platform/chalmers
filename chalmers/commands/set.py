'''
'''
from __future__ import unicode_literals, print_function

import logging

from chalmers.program import Program
from chalmers.utils import try_eval, set_nested_key
from chalmers import errors


log = logging.getLogger('chalmers.set')


def main(args):

    proc = Program(args.name)

    if proc.is_running:
        log.warning("Program is running: Updates will not be reflected until a restart is done")

    if args.key == 'name':
        raise errors.ChalmersError("Can not set program name")

    set_nested_key(proc.raw_data, args.key, args.value)
    proc.save()

    log.info("Set '%s' to %r for program %s" % (args.key, args.value, args.name))


def add_parser(subparsers):
    parser = subparsers.add_parser('set',
                                      help='Set a variable in the program definition',
                                      description=__doc__)

    parser.add_argument('name', metavar='PROG')
    parser.add_argument('key')
    parser.add_argument('value', type=try_eval)
    parser.set_defaults(main=main, state='pause')
