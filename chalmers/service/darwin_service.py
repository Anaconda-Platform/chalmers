"""
Install a launchd rule to run at system boot 
"""
from __future__ import unicode_literals, print_function

import logging
from subprocess import check_output, check_call, CalledProcessError
import sys

from chalmers import errors


# chalmers_plist = """
# <?xml version="1.0" encoding="UTF-8"?>
# <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
# <plist version="1.0">
# <dict>
#     <key>Label</key>
#     <string>org.continuum.chalmers</string>
#     <key>ProgramArguments</key>
#     <array>
#         <string>{python_exe}</string>
#         <string>{chalmers_script}</string>
#         <string>start</string>
#         <string>-a</string>
#     </array>
#     <key>RunAtLoad</key>
#     <true/>
# </dict>
# </plist>
# """.format(python_exe=sys.executable, chalmers_script=sys.argv[0])
launchd_label = "org.binstar.chalmers"

log = logging.getLogger('chalmers.reboot')

def get_launchd():
    try:
        return check_output(['launchctlddd', 'list', launchd_label])
    except OSError as err:
        raise errors.ChalmersError("Could not access program 'launchctl' required for osx service install")
    except CalledProcessError as err:
        if err.returncode == 1:
            # launchd_label was not found
            return None
        raise


def add_launchd():
    try:
        chalmers_script = sys.argv[0]
        command = ['launchctl', 'submit', '-l', launchd_label, '--',
                   sys.executable, chalmers_script, 'start', '--all']
        log.info("Running command: %s" % ' '.join(command))
        output = check_output(command).strip()
        log.info("launchctl: " % output)
    except OSError as err:
        raise errors.ChalmersError("Could not access program 'launchctl' required for osx service install")
    except CalledProcessError as err:
        if err.returncode == 1:
            # launchd_label was not found
            raise errors.ChalmersError("Chalmers service is already installed")
        raise


def install(args):
    """Create a launchd plist and load as a global daemon"""

    log.info("Adding chalmers launchd plist")
    add_launchd()
    log.info("All chalmers programs will now run on boot")

def uninstall(args):
    """Uninstall launchd plist for chalmers"""

    log.info("Removing chalmers plist from launchd")
    try:
        command = ['launchctl', 'remove', 'org.continuum.chalmers']
        log.info("Running command: %s" % ' '.join(command))
        output = check_output(command).strip()
    except CalledProcessError as err:
        if err.returncode == 1:
            raise errors.ChalmersError("Chalmers service is not installed")
        raise
    else:
        log.info("Chalmers service has been removed")

def status(args):
    """Check if chalmers will be started at reboot"""

    launchd_lines = get_launchd()
    print(launchd_lines)
    if launchd_label in launchd_lines:
        log.info("Chalmers is setup to start on boot")
    else:
        log.info("Chalmers will not start on boot")

