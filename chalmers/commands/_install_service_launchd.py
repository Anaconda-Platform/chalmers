"""
Install a crontab rule to run at system boot 
"""
from __future__ import unicode_literals, print_function

import logging
from subprocess import Popen, check_output, CalledProcessError, PIPE
import sys, os

from chalmers import errors

chalmers_plist = """
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>org.binstar.chalmers</string>
    <key>ProgramArguments</key>
    <array>
        <string>{python_exe}</string>
        <string>{chalmers_script}</string>
        <string>start</string>
        <string>-a</string>        
    </array>
    <key>RunAtLoad</key>
    <true/>
</dict>
</plist>
""".format(python_exe=sys.executable, chalmers_script=sys.argv[0])

launchd_dir = "/Library/LaunchDaemons"
launchd_label = "org.binstar.chalmers"
launchd_filename = os.path.join(launchd_dir, launchd_label + ".plist")

log = logging.getLogger('chalmers.reboot')

def get_launchd():
    try:
        output = check_output(['launchctl', 'list']).strip()
    except CalledProcessError as err:
        if err.returncode != 1:
            raise errors.ChalmersError("Could not access launchctl")
        return []
    return output

def add_launchd():
    with open(launchd_filename, "w") as fH:
        fH.write(chalmers_plist)
    try:
        output = check_output(['launchctl', 'load', launchd_filename]).strip()
    except CalledProcessError as err:
        if err.returncode != 1:
            raise errors.ChalmersError("Could not access launchctl")
        return []

def check_if_root():
    if os.getuid() != 0:
        log.info("chalmers service must be run via sudo on OS X.")
        return False
    else:
         return True
    
def main(args):
    """Create a launchd plist and load as a global daemon"""
    if not check_if_root():
        return
        
    launchd_lines = get_launchd()
    if launchd_label in launchd_lines:
        log.info("Chalmers launchd plist already loaded")
    else:
        log.info("Adding chalmers launchd plist")
        add_launchd()
        log.info("All chalmers programs will now run on boot")

def main_uninstall(args):
    """Uninstall launchd plist for chalmers"""
    if not check_if_root():
        return

    launchd_lines = get_launchd()
    if launchd_label in launchd_lines:
        log.info("Removing chalmers plist from launchd")
        try:
            output = check_output(['launchctl', 'unload', launchd_filename]).strip()
        except CalledProcessError as err:
            if err.returncode != 1:
                raise errors.ChalmersError("Could not access launchctl")
        os.remove(launchd_filename)
    else:
        log.info("Chalmers launchd plist not loaded")

def main_status(args):
    """Check if chalmers will be started at reboot"""
    if not check_if_root():
        return
        
    launchd_lines = get_launchd()
    if launchd_label in launchd_lines:
        log.info("Chalmers is setup to start on boot")
    else:
        log.info("Chalmers will not start on boot")

