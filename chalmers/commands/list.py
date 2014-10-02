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

def sort_key(prog):
    return prog.text_status, prog.name

def main(args):

    programs = sorted(Program.find_for_user(), key=sort_key)

    for prog in programs:

        if prog.is_running:
            start_time = prog.state.get('start_time')
            if start_time:
                td = str(timedelta(seconds=(time.time() - start_time))).rsplit('.', 1)[0]
            else:
                td = '?'
            ctx = (prog.data['name'][:24], prog.text_status,
                   prog.state.get('child_pid'),
                   td,
                )

            print('%-25s %-15s pid %-6s, uptime %s' % ctx)
        else:
            stop_time = prog.state.get('stop_time')
            if stop_time:
                td = 'downtime ' + str(timedelta(seconds=(time.time() - stop_time))).rsplit('.', 1)[0]
            else:
                td = ''

            reason = prog.state.get('reason', '')
            ctx = (prog.data['name'][:35], prog.text_status,
                   reason

                  )

            print('%-25s %-15s %s' % ctx)

            if td:
                print(' ' * 41, td)

    if not programs:
        print('No programs added')


def add_parser(subparsers):
    parser = subparsers.add_parser('list',
                                      help='List registered programs',
                                      description=__doc__,
                                      formatter_class=RawDescriptionHelpFormatter)

    parser.set_defaults(main=main)
