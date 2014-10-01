'''
'''
from __future__ import unicode_literals, print_function

from argparse import FileType
import logging
from os import path
import os

import yaml

from chalmers.config import dirs
from chalmers.utils.definition import make_definition


log = logging.getLogger('chalmers.import')



def main(args):

    import_data = yaml.safe_load(args.input)
    groups = {k['group']['name']:k['group'] for k in import_data if 'group' in k}
    programs = {k['program']['name']:k['program'] for k in import_data if 'program' in k}

    for group in groups.values():
        group_dir = path.join(dirs.user_data_dir, 'groups')
        if not path.isdir(group_dir): os.makedirs(group_dir)

        group_path = path.join(group_dir, '%s.yaml' % group['name'])
        log.info("Writing group %s to %s" % (group['name'], group_path))
        with open(group_path, 'w') as gf:
            yaml.safe_dump(group, gf, default_flow_style=False)

    for program in programs.values():
        program = make_definition(program)
        program_dir = path.join(dirs.user_data_dir, 'programs')
        if not path.isdir(program_dir): os.makedirs(program_dir)

        program_path = path.join(program_dir, '%s.yaml' % program['name'])
        log.info("Writing program %s to %s" % (program['name'], program_path))

        with open(program_path, 'w') as pf:
            yaml.safe_dump(program, pf, default_flow_style=False)

def add_parser(subparsers):
    parser = subparsers.add_parser('import',
                                      help='[IN DEVELOPMENT] Batch import many commands from a yaml file',
                                      description=__doc__)

    parser.add_argument('input', type=FileType('r'))
    parser.set_defaults(main=main)
