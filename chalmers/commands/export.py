'''
'''
from __future__ import unicode_literals, print_function

from argparse import FileType
import logging
import sys

import yaml

from chalmers.program import Program


log = logging.getLogger('chalmers.export')



def main(args):

    export_data = []

    for prog in Program.find_for_user():
        export_data.append({'program': prog.raw_data})

    yaml.safe_dump(export_data, args.output, default_flow_style=False)

def add_parser(subparsers):
    parser = subparsers.add_parser('export',
                                      help='[IN DEVELOPMENT] Export current configuration to be installed with the "import" command',
                                      description=__doc__)

    parser.add_argument('names', nargs='*')
    parser.add_argument('-o', '--output', type=FileType('w'), default=sys.stdout)
    parser.set_defaults(main=main)
