'''
'''
from __future__ import unicode_literals, print_function

from pprint import pformat
from chalmers.program import Program
import logging
log = logging.getLogger('chalmers.show')

def pformat2(value):
    pvalue = pformat(value, width=66).split('\n')
    sep = '\n' + ' ' * 14
    return sep.join(pvalue)

def print_opts(category, data, opts):
    if not any(opt in data for opt in opts):
        return
    log.info('\n%s' % category)
    log.info('-' * len(category))
    for opt in opts:
        if opt in data:
            value = data.pop(opt)
            print("%12s: %s" % (opt, pformat2(value)))

def main(args):

    prog = Program(args.name)
    print("Definition file:\n\t%s" % prog.definition_filename)
    print("State file:\n\t%s" % prog.state_filename)
    print('State')
    for key, value in prog.state.items():
        print("%12s: %s" % (key, value))

    # print('running' prog.is_running)

    if args.raw:
        data = prog.raw_data.copy()
    else:
        data = prog.data.copy()

    for category, opts in Program.OPTIONS:
        print_opts(category, data, opts)

    print_opts('Other Options', data, data.keys())


def add_parser(subparsers):
    parser = subparsers.add_parser('show',
                                      help='Show command',
                                      description=__doc__)

    parser.add_argument('-n', '--name', required=True)
    parser.add_argument('-r', '--raw', action='store_true')
    parser.set_defaults(main=main)
