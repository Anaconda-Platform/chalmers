'''
Allow a program to run in the background 

Example:
    From a terminal 'window 1' run::
    
      $ chalmers start --wait server1
    
    program output ...
    program output ...
    
    From another Another terminal 'window 2' run::
      
      $ chalmers bg server1
    
    Now you will be able to close the terminal 'window 1' without shutting down your server

'''
from __future__ import unicode_literals, print_function

from argparse import RawDescriptionHelpFormatter
import logging

from chalmers import errors
from chalmers.program import Program


log = logging.getLogger('chalmers.edit')


def main(args):

    prog = Program(args.name)

    if not prog.is_running:
        raise errors.StateError("Program is not running")

    prog.send('bg')
    print("Process is now a background process")

def add_parser(subparsers):
    description = 'Allow a service to run in the background'
    parser = subparsers.add_parser('bg',
                                   help=description, description=description,
                                   epilog=__doc__,
                                   formatter_class=RawDescriptionHelpFormatter)

    parser.add_argument('name')
    parser.set_defaults(main=main)
