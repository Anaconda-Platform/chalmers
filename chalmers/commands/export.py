'''
'''
from __future__ import unicode_literals, print_function
from ast import literal_eval
from chalmers import errors
from chalmers.config import dirs
from chalmers.program import Program
from os import path
import logging
from argparse import FileType
import sys
import yaml


log = logging.getLogger('chalmers.export')



def main(args):

    export_data = []
    for group in Program.find_groups_for_user():
        export_data.append({'group': group})

    for prog in Program.find_for_user():
        export_data.append({'program': prog.raw_data})

    yaml.safe_dump(export_data, args.output, default_flow_style=False)

def add_parser(subparsers):
    parser = subparsers.add_parser('export',
                                      help='Add a command to run',
                                      description=__doc__)

    parser.add_argument('names', nargs='*')
    parser.add_argument('-o', '--output', type=FileType('w'), default=sys.stdout)
    parser.set_defaults(main=main)
