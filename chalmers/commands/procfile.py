'''
Run all programs in a procfile 
example:

    chalmers procfile
'''
from __future__ import unicode_literals, print_function

from argparse import RawDescriptionHelpFormatter
import logging
from os import path
import os
import shlex

import yaml

from chalmers import config, errors
from chalmers.program import Program
from chalmers.utils import cli
from chalmers.utils.mutiplex_io_pool import MultiPlexIOPool
from pprint import pprint


log = logging.getLogger('chalmers.procfile')

split = lambda item: shlex.split(item, posix=os.name == 'posix')
def main(args):

    config.set_relative_dirs(path.abspath('.chalmers'))
    if not os.path.isfile(args.procfile):
        raise errors.ChalmersError("procfile '{}' does not exist".format(args.procfile))

    with open(args.procfile) as fd:
        procs = yaml.load(fd)
    print('procs', procs)
    programs = []
    for name, command in procs.items():
        definition = {
          'name': name,
          'command': split(command),

        }
        program = Program(name)
        pprint(definition)
        program.raw_data.update(definition)
        programs.append(program)

    pool = MultiPlexIOPool(stream=True, use_color=args.color)

    for prog in programs:
        pool.append(prog)

    pool.join()



def add_parser(subparsers):
    parser = subparsers.add_parser('procfile',
                                      help='Start a program',
                                      description=__doc__,
                                      formatter_class=RawDescriptionHelpFormatter)

    parser.add_argument('-f', '--procfile',
                        default='Procfile',
                        help='procfile path (default: %(default)s)')
    cli.add_selection_group(parser)

    parser.set_defaults(main=main)
