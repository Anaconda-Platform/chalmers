'''
'''
from __future__ import unicode_literals, print_function

import logging

from chalmers.program import Program
from datetime import timedelta
import time


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
                                      help='List registered commands',
                                      description=__doc__)

    parser.set_defaults(main=main)
