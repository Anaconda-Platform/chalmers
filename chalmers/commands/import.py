'''
[Advanced] [In-development]

import a file exported with `chalmers export`


'''
from __future__ import unicode_literals, print_function

from argparse import FileType
import logging
from os import path
import os

import yaml

from chalmers import config, errors
from chalmers.program import Program


log = logging.getLogger('chalmers.import')


def main(args):

    import_data = yaml.safe_load(args.input)
    groups = {k['group']['name']:k['group'] for k in import_data if 'group' in k}
    programs = {k['program']['name']:k['program'] for k in import_data if 'program' in k}

    for group in groups.values():
        group_dir = path.join(config.dirs.user_data_dir, 'groups')
        if not path.isdir(group_dir): os.makedirs(group_dir)

        group_path = path.join(group_dir, '%s.yaml' % group['name'])
        log.info("Writing group %s to %s" % (group['name'], group_path))
        with open(group_path, 'w') as gf:
            yaml.safe_dump(group, gf, default_flow_style=False)

    for defn in programs.values():
        if 'name' not in defn:
            raise errors.ChalmersError("Import definition requires a name field")

        prog = Program(defn['name'])
        if prog.exists():
            log.warn("Program '%s' already exists, not importing" % defn['name'])
            continue

        prog.raw_data.update(defn)
        prog.mk_data()

def add_parser(subparsers):
    parser = subparsers.add_parser('import',
                                      help='[IN DEVELOPMENT] Batch import many commands from a yaml file',
                                      description=__doc__)

    parser.add_argument('input', type=FileType('r'))

    parser.set_defaults(main=main)
