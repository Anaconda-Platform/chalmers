'''
Edit a program definition

Open the program definition file with the 
EDITOR environment variable

for example:
    
    chalmers edit server1
'''
from __future__ import unicode_literals, print_function

from argparse import RawDescriptionHelpFormatter
import logging
import os
import pipes
import subprocess

from chalmers import errors
from chalmers.program import Program


log = logging.getLogger('chalmers.edit')


def main(args):

    EDITOR = os.environ.get('EDITOR', None)
    if EDITOR is None:
        raise errors.ChalmersError("Environment variable 'EDITOR' needs to be set")

    prog = Program(args.name, force=True)

    cmd = '%s %s' % (EDITOR, pipes.quote(prog.raw_data.filename))

    print(cmd)
    if subprocess.call(cmd, shell=True):
        raise errors.ChalmersError('Command "%s" exited with non zero status' % cmd)

    if prog.is_running:
        log.info("Changes to program %s will take effect on the next restart" % prog.name)

def add_parser(subparsers):
    parser = subparsers.add_parser('edit',
                                      help='Edit a service definition',
                                      description=__doc__,
                                      formatter_class=RawDescriptionHelpFormatter)

    parser.add_argument('name')
    parser.set_defaults(main=main)
