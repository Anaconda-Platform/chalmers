import unittest

from chalmers.service.cron_service import CronService, check
from contextlib import contextmanager
from chalmers import errors
import subprocess as sp
crontab_lines = None

def mock_check_output(*args, **kwargs):
    if crontab_lines is None:
        raise sp.CalledProcessError(1, 'crontab', 'crontab: no crontab for test')
    return crontab_lines

def mock_communicate(input):
    global crontab_lines
    crontab_lines = input
    return ''

class Test(unittest.TestCase):

    @contextmanager
    def mock_crontab(self, exists=True):
        from mock import patch
        patch1 = patch('subprocess.check_output')
        patch2 = patch('subprocess.Popen')
        with patch1 as check_output, patch2 as Popen:
            if  exists:
                check_output.side_effect = mock_check_output
                Popen().communicate.side_effect = mock_communicate
            else:
                check_output.side_effect = IOError(2, "err")
            yield

    def test_install(self):

        with self.mock_crontab(exists=True):

            service = CronService(False)
            self.assertFalse(service.status())
            self.assertTrue(service.install())
            self.assertTrue(service.status())
            self.assertTrue(service.uninstall())
            self.assertFalse(service.status())

    def test_check(self):
        global crontab_lines

        with self.mock_crontab(exists=False):
            self.assertFalse(check())

        with self.mock_crontab(exists=True):
            self.assertTrue(check())

            crontab_lines = 'some content'

            self.assertTrue(check())






if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.test_status']
    unittest.main()
