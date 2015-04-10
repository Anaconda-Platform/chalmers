"""
Install windows startup script
"""
from __future__ import print_function, absolute_import, unicode_literals

import logging
from os import path
import os
import sys

from win32api import GetUserName


log = logging.getLogger(__name__)

HOME = os.environ.get('HOMEPATH')
STARTUP_DIR = path.join(HOME, 'AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup')

class Win32LocalService(object):

    @property
    def script_path(self):
        return path.join(STARTUP_DIR, 'chalmers.bat')

    def install(self):

        chalmers_script = sys.argv[0]
        command = [sys.executable, chalmers_script, 'start', '--all']

        with open(self.script_path, 'w') as fd:
            log.info("Write file: %s" % self.script_path)
            print(' '.join(command), file=fd)

        log.info("All chalmers programs will now run on login")



    def uninstall(self):

        if os.path.exists(self.script_path):
            log.info("Remvoe File: %s" % self.script_path)
            os.unlink(self.script_path)
        else:
            log.warning("File: %s does not exst" % self.script_path)

        log.info("Chalmers local service has been removed")


    def status(self):
        log.info("Check if file exists: %s" % self.script_path)
        if os.path.exists(self.script_path):
            log.info("Chalmers is setup to start on boot")
        else:
            log.info("Chalmers will not start on boot")

