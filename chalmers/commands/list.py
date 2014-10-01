'''List the all the defined programs

eg: 

    $ chalmers list
    server1                             RUNNING         pid 19278 , uptime 0:10:01

    
'''
from __future__ import unicode_literals, print_function

from argparse import RawDescriptionHelpFormatter
from datetime import timedelta
import logging
import time

from chalmers.program import Program


log = logging.getLogger(__name__)

def main(args):

    programs = list(Program.find_for_user())

    for prog in programs:

        if prog.is_running:
            start_time = prog.state.get('start_time')
            td = str(timedelta(seconds=(time.time() - start_time))).rsplit('.', 1)[0]
            ctx = (prog.data['name'][:35], prog.text_status,
                   prog.state.get('child_pid'),
                   td,
                )

            print('%-35s %-15s pid %-6s, uptime %s' % ctx)
        else:
            ctx = (prog.data['name'][:35], prog.text_status,
                   prog.state.get('reason')
                  )

            print('%-35s %-15s %s' % ctx)

    if not programs:
        print('No programs added')


def add_parser(subparsers):
    parser = subparsers.add_parser('list',
                                      help='List registered programs',
                                      description=__doc__,
                                      formatter_class=RawDescriptionHelpFormatter)

    parser.set_defaults(main=main)
