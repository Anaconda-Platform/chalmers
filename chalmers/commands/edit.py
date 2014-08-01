'''
Edit a service definition
'''
from __future__ import unicode_literals, print_function
from chalmers.program import Program
import logging
from argparse import FileType
import sys
import yaml
import os
from chalmers import errors
import subprocess
import pipes


log = logging.getLogger('chalmers.edit')


def main(args):

    EDITOR = os.environ.get('EDITOR', None)
    if EDITOR is None:
        raise errors.ChalmersError("Environment variable 'EDITOR' needs to be set")

    prog = Program(args.name)

    cmd = '%s %s' % (EDITOR, pipes.quote(prog.definition_filename))

    print(cmd)
    if subprocess.call(cmd, shell=True):
        raise errors.ChalmersError('Command "%s" exited with non zero status' % cmd)


def add_parser(subparsers):
    parser = subparsers.add_parser('edit',
                                      help='Edit a service definition',
                                      description=__doc__)

    parser.add_argument('name')
    parser.set_defaults(main=main)
