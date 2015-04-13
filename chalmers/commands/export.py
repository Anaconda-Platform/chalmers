'''
[Advanced] [In-development]

Export a program list to a single yaml file.

The export may contain machine specific paths.
and may need to be edited for portability
'''

from __future__ import unicode_literals, print_function

from argparse import FileType
import logging
import sys

import yaml

from chalmers.utils.cli import add_selection_group, select_programs


log = logging.getLogger('chalmers.export')



def main(args):

    export_data = []

    programs = select_programs(args, filter_paused=False)

    for prog in programs:
        export_data.append({'program': dict(prog.raw_data)})

    yaml.safe_dump(export_data, args.output, default_flow_style=False)

def add_parser(subparsers):
    parser = subparsers.add_parser('export',
                                      help='[IN DEVELOPMENT] Export current configuration to be installed with the "import" command',
                                      description=__doc__)

    add_selection_group(parser)

    parser.add_argument('-o', '--output', type=FileType('w'), default=sys.stdout)
    parser.set_defaults(main=main)
