'''
'''
from __future__ import unicode_literals, print_function
from ast import literal_eval
from chalmers import errors
from chalmers.config import dirs
from chalmers.program import Program
from os import path
import logging


log = logging.getLogger('chalmers.set')


def set_nested_key(dct, key, value):
    keys = key.split('.')
    next_key = keys.pop(0)

    while keys:
        dct = dct.setdefault(next_key, {})
        next_key = keys.pop(0)

    dct[next_key] = value
    pass


def main(args):

    proc = Program(args.name)

    if proc.is_running:
        log.warning("Program is running: Updates will not be reflected until a restart is done")

    set_nested_key(proc.raw_data, args.key, args.value)
    proc.save()

    log.info("Set '%s' to %r for program %s" % (args.key, args.value, args.name))

def smart_type(value):
    try:
        return literal_eval(value)
    except:
        return value

def add_parser(subparsers):
    parser = subparsers.add_parser('set',
                                      help='Add a command to run',
                                      description=__doc__)

    parser.add_argument('-n', '--name', required=True)
    parser.add_argument('key')
    parser.add_argument('value', type=smart_type)
    parser.set_defaults(main=main, state='pause')
