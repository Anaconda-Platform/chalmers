'''
Set a definition variable for a program

To update a programs environment 
run:

    chalmers set server1 env.PORT=5000
    
Common Config values:

  * startsecs: The time in seconds that the program is assumed to be starting up
    If the program exits before this time it is considered to be spinning
  * startretries: The number or times to launch a spinning program
  * stopwaitsecs: Wait this long
  * exitcodes: A list of exit codes that are accepted as a successfull exit 
  * stopsignal: The signal to sent to terminate the program. May be an int or string
    eg: 'SIGTERM' or 15  

 * log_dir: The base directory to output logs
 * redirect_stderr: Direct stderr to the same log file as stdout
 * stdout: filename to pipe the program's stdout
 * stderr: filename to pipe the program's stderr
 * daemon_log: filename to pipe the programs conrol log 
 
'''
from __future__ import unicode_literals, print_function

import logging

from chalmers.program import Program
from chalmers.utils import try_eval, set_nested_key
from chalmers import errors
from argparse import RawDescriptionHelpFormatter


log = logging.getLogger('chalmers.set')

def split_try_eval(item):

    if '=' not in item:
        raise TypeError("Chalmers can not set '%s' as a definition variable\n"
                        "The parameter must contain an '='" % (item))
    key, value = item.split('=', 1)
    return key, try_eval(value)

def main(args):

    proc = Program(args.name)

    if proc.is_running:
        log.warning("Program is running: Updates will not be reflected until a restart is done")

    for key, value in args.items:
        if key == 'name':
            raise errors.ChalmersError("Can not set program name")

        set_nested_key(proc.raw_data, key, value)
        log.info("Set '%s' to %r for program %s" % (key, value, args.name))

    proc.mk_data()
    proc.save()

    log.info("done")


def add_parser(subparsers):
    parser = subparsers.add_parser('set',
                                      help='Set a variable in the program definition',
                                      description=__doc__,
                                      formatter_class=RawDescriptionHelpFormatter)

    parser.add_argument('name', metavar='PROG',
                        help='The name of the program to update')
    parser.add_argument('items', nargs='+', metavar='KEY=VALUE', type=split_try_eval,
                        help='Update the program with these key-value pairs')
    parser.set_defaults(main=main)
