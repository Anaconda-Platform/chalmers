"""
Install a crontab rule to run at system boot 
"""
from __future__ import unicode_literals, print_function

import logging
from subprocess import Popen, check_output, CalledProcessError, PIPE
import sys

from chalmers import errors


python_exe = sys.executable
chalmers_script = sys.argv[0]
chalmers_tab_entry = '@reboot %s %s start -a' % (python_exe, chalmers_script)

log = logging.getLogger('chalmers.reboot')

def get_crontab():
    try:
        output = check_output(['crontab', '-l']).strip()
    except CalledProcessError as err:
        if err.returncode != 1:
            raise errors.ChalmersError("Could not read crontab")
        return []

    return output.split('\n')

def set_crontab(tab):

    new_cron_tab = '\n'.join(tab) + '\n'

    p0 = Popen(['crontab'], stdin=PIPE)
    p0.communicate(input=new_cron_tab)

def main(args):
    tab_lines = get_crontab()

    if chalmers_tab_entry in tab_lines:
        log.info("Chalmers crontab instruction already exists")
    else:
        log.info("Adding chalmers instruction to crontab")
        tab_lines.append(chalmers_tab_entry)

        set_crontab(tab_lines)

        log.info("All chalmers programs will now run on boot")

def main_uninstall(args):

    tab_lines = get_crontab()

    if chalmers_tab_entry in tab_lines:
        log.info("Removing chalmers instruction from crontab")
        tab_lines.remove(chalmers_tab_entry)

        set_crontab(tab_lines)

    else:
        log.info("Chalmers crontab instruction does not exist")

def main_status(args):

    tab_lines = get_crontab()

    if chalmers_tab_entry in tab_lines:
        log.info("Chalmers is setup to start on boot")
    else:
        log.info("Chalmers will not start on boot")

