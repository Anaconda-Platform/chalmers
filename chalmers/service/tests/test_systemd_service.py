from contextlib import contextmanager
import tempfile
import unittest

from chalmers.service.systemd_service import SystemdService, check
from chalmers.service import systemd_service
import subprocess as sp
from os import path

enabled = {}

def mock_check_output(command, *args, **kwargs):
    if command[:2] == ['systemctl', 'is-enabled']:
        if command[2] not in enabled:
            raise sp.CalledProcessError(1, 'systemctl', 'not found')
        return 'ok'
    elif command[:2] == ['systemctl', 'enable']:

        configfile = path.join(systemd_service.SYSTEM_D_INIT_DIR, command[2])
        if not path.exists(configfile):
            raise sp.CalledProcessError(1, 'systemctl', 'not found')
        enabled[command[2]] = True

    elif command[:2] == ['systemctl', 'disable']:

        configfile = path.join(systemd_service.SYSTEM_D_INIT_DIR, command[2])
        if not path.exists(configfile):
            raise sp.CalledProcessError(1, 'systemctl', 'not found')

        del enabled[command[2]]
        return 'ok'
    else:
        raise Exception('unknown command %r' % command)

class Test(unittest.TestCase):

    @contextmanager
    def mock_systemd(self, exists=True):
        from mock import patch
        patch1 = patch('subprocess.check_output')
        patch2 = patch('os.getuid')


        with patch1 as check_output, patch2 as getuid:
            SYSTEM_D_INIT_DIR = systemd_service.SYSTEM_D_INIT_DIR
            systemd_service.SYSTEM_D_INIT_DIR = tempfile.mkdtemp()

            try:
                getuid.return_value = 0

                if  exists:
                    check_output.side_effect = mock_check_output
                else:
                    check_output.side_effect = IOError(2, "err")
                yield
            finally:
                systemd_service.SYSTEM_D_INIT_DIR = SYSTEM_D_INIT_DIR


    def test_install(self):

        with self.mock_systemd(exists=True):

            service = SystemdService(None)
            self.assertFalse(service.status())
            self.assertTrue(service.install())
            self.assertTrue(service.status())
            self.assertTrue(service.uninstall())
            self.assertFalse(service.status())
            self.assertFalse(service.uninstall())



if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.test_status']
    unittest.main()
